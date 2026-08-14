#!/usr/bin/env bash
source ./scripts/compile/helpers/get_java.sh
uv run buildozer android debug deploy run
adb logcat | grep python
