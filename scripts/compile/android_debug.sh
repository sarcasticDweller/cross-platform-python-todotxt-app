#!/usr/bin/env bash
<<<<<<< HEAD
./scripts/compile/helper/get_java.sh
=======
./scripts/copmile/helpers/get_java.sh
>>>>>>> f7f0aa5b2eb487bf71f4ef9c47781735ea79db54
uv run buildozer android debug deploy run
adb logcat | grep python
