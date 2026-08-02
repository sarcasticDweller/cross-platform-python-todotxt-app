#!/usr/bin/env bash
#
# setup_dev_env.sh, made by Claude.
#
# Same job as setup_pyenv_env_as_root.sh (project root + Python 3.11.2 + venv
# + dependencies), but backed by uv + pyproject.toml/uv.lock instead of
# pyenv/apt/requirements.txt. uv fetches a prebuilt Python interpreter, so
# there's no build-essential/libssl-dev/etc apt block needed, and no
# compiling Python from source. `uv sync` resolves the whole dependency
# graph from uv.lock (generating it from pyproject.toml on first run),
# so installs are reproducible across machines, not just direct-pin-deep
# like requirements.txt was.
#
# Idempotent: every step checks "does this already exist / is this already
# correct?" before doing anything, and nothing destructive ever runs
# automatically.
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON_VERSION="3.11.15" # kept in lockstep with setup_pyenv_env_as_root.sh's pin
VENV_DIR="$PROJECT_ROOT/.venv" # named to match pyrightconfig.json's venv path
JDK_VERSION="17" # matches Buildozer's own tested/CI JDK; pulled from Adoptium (apt) or the temurin cask (Homebrew) so it's the same JDK build either way

if [ "$PWD" != "$PROJECT_ROOT" ]; then
  echo "This script must be run from the project root folder: $PROJECT_ROOT" >&2
  echo "Current directory: $PWD" >&2
  echo "Try: cd \"$PROJECT_ROOT\" && \"$SCRIPT_DIR/setup_sans_pain.sh\"" >&2
  exit 1
fi

echo "== 1. uv installation =="

if command -v uv >/dev/null 2>&1; then
  echo "uv already installed, skipping install."
else
  echo "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

echo "== 2. Install Python $PYTHON_VERSION via uv =="

if uv python list --only-installed 2>/dev/null | grep -q "$PYTHON_VERSION"; then
  echo "Python $PYTHON_VERSION already installed under uv, skipping."
else
  echo "Fetching prebuilt Python $PYTHON_VERSION..."
  uv python install "$PYTHON_VERSION"
fi

echo "== 3. Pin project to $PYTHON_VERSION =="

CURRENT_PIN="$(cat "$PROJECT_ROOT/.python-version" 2>/dev/null || echo "")"
if [ "$CURRENT_PIN" = "$PYTHON_VERSION" ]; then
  echo ".python-version already pins $PYTHON_VERSION, skipping."
else
  uv python pin "$PYTHON_VERSION"
  echo "Pinned this directory to $PYTHON_VERSION."
fi

echo "== 4. Sync venv + dependencies from pyproject.toml/uv.lock =="

# `uv sync` creates $VENV_DIR if missing (using the pinned Python) and
# resolves/installs the exact locked dependency graph into it. It generates
# uv.lock from pyproject.toml on first run if no lock exists yet. Unlike the
# old script's "leave an existing venv alone" step, this actively reconciles
# the venv's installed packages to match the lock every run — that's the
# point of switching to a lockfile, so don't be surprised by it.
export UV_PROJECT_ENVIRONMENT="$VENV_DIR"
uv sync

echo "== 5. Buildozer system dependencies =="

# These are host-side tools Buildozer/python-for-android need to build the
# Android APK (Buildozer itself still downloads its own Android SDK/NDK on
# first `buildozer android debug`). Branches on OS so re-runs stay a no-op
# on either side (dpkg -s / brew list checks).
OS_NAME="$(uname -s)"

if [ "$OS_NAME" = "Darwin" ]; then
  if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew not found — install it from https://brew.sh, then re-run this script." >&2
    exit 1
  fi

  if xcode-select -p >/dev/null 2>&1; then
    echo "Xcode Command Line Tools already installed, skipping (build-essential equivalent)."
  else
    echo "Installing Xcode Command Line Tools (build-essential equivalent)..."
    echo "This pops a GUI installer — finish it, then re-run this script."
    xcode-select --install
    exit 1
  fi

  # Maps the Debian package list below onto Homebrew. git/zip/unzip/zlib/
  # ncurses ship with macOS already, so they're left out here. adb comes from
  # the android-platform-tools cask instead of Debian's platform-tools-installer.
  REQUIRED_FORMULAE="autoconf automake libtool pkg-config cmake gettext ccache libffi openssl@3"
  REQUIRED_CASKS="temurin@${JDK_VERSION} android-platform-tools"

  MISSING_FORMULAE=""
  for pkg in $REQUIRED_FORMULAE; do
    if ! brew list --formula "$pkg" >/dev/null 2>&1; then
      MISSING_FORMULAE="$MISSING_FORMULAE $pkg"
    fi
  done
  if [ -z "$MISSING_FORMULAE" ]; then
    echo "All Buildozer build-dep formulae already present, skipping."
  else
    echo "Installing missing formulae:$MISSING_FORMULAE"
    # shellcheck disable=SC2086
    brew install $MISSING_FORMULAE
  fi

  MISSING_CASKS=""
  for pkg in $REQUIRED_CASKS; do
    if ! brew list --cask "$pkg" >/dev/null 2>&1; then
      MISSING_CASKS="$MISSING_CASKS $pkg"
    fi
  done
  if [ -z "$MISSING_CASKS" ]; then
    echo "All Buildozer build-dep casks already present, skipping."
  else
    echo "Installing missing casks:$MISSING_CASKS"
    # shellcheck disable=SC2086
    brew install --cask $MISSING_CASKS
  fi

elif command -v apt-get >/dev/null 2>&1; then
  JDK_PKG="temurin-${JDK_VERSION}-jdk"

  # Debian's own repos ship a different, non-overlapping JDK major per release
  # (bookworm: only 17, trixie: only 21+), and Buildozer's own CI/Dockerfile
  # only ever test against JDK 17 — so pull it from Eclipse Temurin/Adoptium's
  # repo instead of Debian's. Adoptium packages the same JDK majors across
  # every Debian/Ubuntu release, independent of what each release carries.
  ADOPTIUM_KEYRING="/etc/apt/keyrings/adoptium.asc"
  ADOPTIUM_LIST="/etc/apt/sources.list.d/adoptium.list"
  CODENAME="$(awk -F= '/^VERSION_CODENAME/{print $2}' /etc/os-release)"
  ADOPTIUM_ENTRY="deb [signed-by=$ADOPTIUM_KEYRING] https://packages.adoptium.net/artifactory/deb $CODENAME main"

  if [ -f "$ADOPTIUM_LIST" ] && grep -qF "$ADOPTIUM_ENTRY" "$ADOPTIUM_LIST"; then
    echo "Adoptium apt repo already configured, skipping."
  else
    echo "Adding Adoptium apt repo for $CODENAME..."
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://packages.adoptium.net/artifactory/api/gpg/key/public -o "$ADOPTIUM_KEYRING"
    echo "$ADOPTIUM_ENTRY" > "$ADOPTIUM_LIST"
  fi

  # Matches kivy/buildozer's own official Dockerfile package list (checked
  # against https://github.com/kivy/buildozer/blob/master/Dockerfile), since
  # p4a recipe builds (libffi, openssl, etc.) need the full autotools chain,
  # not just the pieces we happened to hit errors for one at a time.
  #
  # adb: Debian's old android-tools-adb package was dropped (its build was
  # too outdated to authenticate with modern Android's ADB protocol), so we
  # need google-android-platform-tools-installer instead, which fetches
  # Google's own platform-tools binary. It lives in the non-free component,
  # which must already be enabled in apt sources for this to resolve.
  REQUIRED_PKGS="git zip unzip $JDK_PKG autoconf automake libtool libltdl-dev \
pkg-config cmake gettext patch build-essential zlib1g-dev libncurses-dev \
libffi-dev libssl-dev ccache google-android-platform-tools-installer"
  MISSING_PKGS=""
  for pkg in $REQUIRED_PKGS; do
    if ! dpkg -s "$pkg" >/dev/null 2>&1; then
      MISSING_PKGS="$MISSING_PKGS $pkg"
    fi
  done
  if [ -z "$MISSING_PKGS" ]; then
    echo "All Buildozer build deps already present, skipping apt."
  else
    echo "Installing missing packages:$MISSING_PKGS"
    apt-get update
    # shellcheck disable=SC2086
    apt-get install -y $MISSING_PKGS
  fi
else
  echo "Neither Homebrew (macOS) nor apt-get (Debian) found — skipping Buildozer build-dep install (adjust this block for your distro if needed)."
fi

echo ""
echo "Done. Activate with:"
echo "    source $VENV_DIR/bin/activate"
echo ""
echo "This machine may have another JDK alongside Temurin $JDK_VERSION, and Gradle's"
echo "daemon picking the wrong one mid-build is a known failure mode. Point Buildozer"
echo "at Temurin explicitly rather than relying on the system default:"
if [ "$OS_NAME" = "Darwin" ]; then
  echo "    JAVA_HOME=\"\$(/usr/libexec/java_home -v $JDK_VERSION)\" uv run buildozer android debug"
else
  echo "    JAVA_HOME=/usr/lib/jvm/temurin-${JDK_VERSION}-jdk-amd64 uv run buildozer android debug"
fi
