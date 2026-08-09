#!/usr/bin/env bash
./scripts/copmile/helpers/get_java.sh
uv run buildozer android debug deploy run
adb logcat | grep python
