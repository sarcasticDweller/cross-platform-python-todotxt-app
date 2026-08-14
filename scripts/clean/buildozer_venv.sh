#!/usr/bin/env bash
# Sometimes `.buildozer/android/platform/.../build/venv gets stale, breaking builds. Its worth deleting it from time to time.
# Notice the `...` there though: the platform *can* change, and this script will break.

rm -rf .buildozer/android/platform/build-arm64-v8a/build/venv
