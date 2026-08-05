#!/usr/bin/env bash
#
# Points Buildozer at Temurin 17 explicitly (see setup_dev_env.sh's closing
# note: this machine may have another JDK installed too, and Gradle's daemon
# picking the wrong one mid-build is a known failure mode).
set -euo pipefail

JDK_VERSION="17"

if [ "$(uname -s)" = "Darwin" ]; then
  JAVA_HOME="$(/usr/libexec/java_home -v "$JDK_VERSION")"
else
  JAVA_HOME="/usr/lib/jvm/temurin-${JDK_VERSION}-jdk-amd64"
fi
export JAVA_HOME

uv run buildozer android debug
