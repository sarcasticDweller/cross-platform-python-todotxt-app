#!/usr/bin/env bash
./scripts/compile/helper/get_java.sh
uv run buildozer android debug deploy run
adb logcat | grep python
