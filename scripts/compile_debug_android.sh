#!/usr/bin/env bash
JAVA_HOME=/usr/lib/jvm/temurin-17-jdk-amd64 uv run buildozer android debug deploy run
adb logcat | grep python
