#!/usr/bin/env bash
set -euo pipefail

# Builds the combined Samsung Galaxy eSIM Service Android APK.
# Requires Android Gradle Plugin access and a local Android SDK (or an
# environment where Gradle can provision the SDK).

gradle :app:assembleDebug
printf '\nDebug APK: %s\n' "$(pwd)/app/build/outputs/apk/debug/app-debug.apk"
