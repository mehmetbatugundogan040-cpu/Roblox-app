# Samsung Galaxy eSIM Service Helper APK

This repository now contains a combined Android APK project for Samsung Galaxy Settings workflows plus the earlier desktop helper source. The APK is designed for people who want one app on a Samsung Galaxy device that opens eSIM, SIM manager, mobile network, data usage, Wi‑Fi, VPN, hotspot/tethering, and app settings pages when the firmware exposes them.

## Important hardware limitation

A **Samsung Galaxy Tab S9 FE+ Wi‑Fi** tablet cannot be turned into a cellular/eSIM tablet by installing an APK. Real eSIM and mobile data require cellular hardware, including a modem, antennas, carrier firmware, an IMEI, and eUICC/SIM support. This service APK can combine settings shortcuts and diagnostics in one launcher app, but Android and Samsung firmware cannot create missing cellular hardware in software.

## Android APK features

- One Samsung-focused launcher app named **Galaxy eSIM Service**.
- Buttons for Samsung/Android network, mobile network, data usage, SIM/eSIM, Wi‑Fi, VPN, hotspot/tethering, and app settings screens.
- A lightweight Android service component so the project is packaged as a service-style APK while keeping all user actions safe and visible.
- Device diagnostics showing telephony, cellular radio, eUICC/eSIM availability, carrier/operator, manufacturer, and model.
- Fallback behavior that opens general Settings or explains when a cellular page is hidden on Wi‑Fi-only firmware.

## Build the APK

The Android project lives in `app/` and can be built with Gradle when the Android Gradle Plugin and Android SDK are available:

```bash
./scripts/build_debug_apk.sh
```

The debug APK output path is:

```text
app/build/outputs/apk/debug/app-debug.apk
```

Install it on a connected Android/Samsung device with:

```bash
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

## Desktop helper

The earlier desktop helper is still available for technicians who want to launch Settings pages over ADB from a computer:

```bash
python src/samsung_esim_settings_app.py
```

No third-party Python package is required for the desktop UI. To launch settings on a connected Android/Samsung device, install Android Platform Tools so `adb` is available on your PATH.

## ADB examples

```bash
adb devices -l
adb shell am start -a android.settings.WIRELESS_SETTINGS
adb shell am start -a android.settings.DATA_USAGE_SETTINGS
adb shell am start -a android.settings.WIFI_SETTINGS
adb shell am start -a android.settings.VPN_SETTINGS
```

If a Settings action fails or opens a generic page, that Samsung firmware or device model does not expose the requested screen. On Wi‑Fi-only Galaxy tablets, SIM manager, eSIM activation, APN, roaming, and mobile data controls may be hidden because the cellular radio stack is not present.
