# Turkey Radio App (No In-App Ads)

This app is an ad-free desktop player UI for Turkish internet radio streams.

## Important technical/legal note

A normal desktop app like this **cannot directly scan/control real RF radio towers** or safely intercept nearby Bluetooth/Wi-Fi/radio signals as a station source.

So this app uses a legal/public internet radio directory (Radio Browser) and loads Turkish stations from the internet.

## Features

- No in-app ad banners/popups added by this app
- Loads large Turkish station list (`countrycode=TR`)
- Search by station/city text
- City filter (includes Istanbul, Mersin, Adana, Gaziantep, Alanya, Antalya, Canakkale, Balikesir when available)
- Play Selected / Stop / Replay

## Run in Visual Studio Code

```bash
pip install -r requirements.txt
python src/turkey_radio_app.py
```

## Build EXE for Windows

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name TurkeyRadio src/turkey_radio_app.py
```

Output:
- `dist/TurkeyRadio.exe`

## Notes

- This app itself does not inject ads; however, some streams may include broadcaster-side audio ads.
- VLC must be installed on Windows for `python-vlc` playback.
