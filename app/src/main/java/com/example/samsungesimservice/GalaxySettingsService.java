package com.example.samsungesimservice;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;

/**
 * Lightweight marker service for installers that expect this APK to behave like a
 * service app. Android does not allow third-party apps to create modem, SIM, or
 * eSIM hardware; the visible settings launchers live in MainActivity.
 */
public class GalaxySettingsService extends Service {
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
