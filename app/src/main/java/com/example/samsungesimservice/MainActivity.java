package com.example.samsungesimservice;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.euicc.EuiccManager;
import android.content.ActivityNotFoundException;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.telephony.TelephonyManager;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

public class MainActivity extends Activity {
    private TextView statusView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setTitle("Galaxy eSIM Service");
        setContentView(buildContent());
        updateStatus();
    }

    private View buildContent() {
        ScrollView scrollView = new ScrollView(this);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        int padding = dp(18);
        root.setPadding(padding, padding, padding, padding);
        scrollView.addView(root);

        TextView title = text("Samsung Galaxy eSIM + Cellular Settings Service", 22, true);
        root.addView(title);
        root.addView(text("Combined APK helper for Samsung Settings shortcuts, eSIM/SIM Manager entry points, mobile network pages, Wi‑Fi, VPN, hotspot, and diagnostics.", 15, false));

        TextView warning = text("Important: a Galaxy Tab S9 FE+ Wi‑Fi model has no cellular modem, IMEI, SIM slot, or eUICC. This APK can show supported Settings pages, but it cannot add real cellular/eSIM service to Wi‑Fi-only hardware.", 15, true);
        warning.setTextColor(Color.rgb(150, 70, 0));
        root.addView(warning);

        statusView = text("Checking device capabilities…", 15, false);
        statusView.setPadding(0, dp(12), 0, dp(12));
        root.addView(statusView);

        addButton(root, "Open Samsung/Android Network Settings", () -> open(Settings.ACTION_WIRELESS_SETTINGS));
        addButton(root, "Open Mobile Network Settings", () -> open(Settings.ACTION_NETWORK_OPERATOR_SETTINGS));
        addButton(root, "Open Data Usage Settings", () -> open(Settings.ACTION_DATA_USAGE_SETTINGS));
        addButton(root, "Open SIM/eSIM Settings", this::openSimOrEsimSettings);
        addButton(root, "Open Wi‑Fi Settings", () -> open(Settings.ACTION_WIFI_SETTINGS));
        addButton(root, "Open VPN Settings", () -> open(Settings.ACTION_VPN_SETTINGS));
        addButton(root, "Open Hotspot/Tethering Settings", this::openTetheringSettings);
        addButton(root, "Open App Settings", () -> openAppSettings());
        addButton(root, "Refresh Capability Check", this::updateStatus);

        root.addView(text("What this service APK can do", 18, true));
        root.addView(text("• Launch supported Samsung/Android Settings pages from one app.\n• Help technicians check whether telephony and eSIM APIs are present.\n• Keep Wi‑Fi, VPN, hotspot, and data-usage shortcuts together for non-cellular tablets.\n• Fall back to general Settings when Samsung firmware hides a cellular page.", 14, false));

        root.addView(text("What Android blocks", 18, true));
        root.addView(text("• Third-party APKs cannot install a modem, create an IMEI, unlock carrier radios, or make a Wi‑Fi-only Galaxy tablet cellular.\n• eSIM activation only works on models with eUICC hardware and carrier provisioning support.", 14, false));
        return scrollView;
    }

    private void updateStatus() {
        PackageManager pm = getPackageManager();
        boolean telephony = pm.hasSystemFeature(PackageManager.FEATURE_TELEPHONY);
        boolean cellular = Build.VERSION.SDK_INT >= 31 && pm.hasSystemFeature(PackageManager.FEATURE_TELEPHONY_RADIO_ACCESS);
        boolean euicc = pm.hasSystemFeature(PackageManager.FEATURE_TELEPHONY_EUICC);
        boolean euiccEnabled = false;
        if (Build.VERSION.SDK_INT >= 28) {
            EuiccManager euiccManager = (EuiccManager) getSystemService(Context.EUICC_SERVICE);
            euiccEnabled = euiccManager != null && euiccManager.isEnabled();
        }
        TelephonyManager telephonyManager = (TelephonyManager) getSystemService(Context.TELEPHONY_SERVICE);
        String networkOperator = telephonyManager == null ? "Unavailable" : blankToUnknown(telephonyManager.getNetworkOperatorName());
        String deviceType = telephony ? "Cellular-capable Android/Samsung device" : "Wi‑Fi-only or telephony-disabled Android device";

        statusView.setText("Device profile: " + deviceType
                + "\nTelephony feature: " + yesNo(telephony)
                + "\nCellular radio access feature: " + yesNo(cellular)
                + "\neUICC/eSIM feature: " + yesNo(euicc)
                + "\neUICC manager enabled: " + yesNo(euiccEnabled)
                + "\nCurrent carrier/operator: " + networkOperator
                + "\nModel: " + Build.MANUFACTURER + " " + Build.MODEL);
    }

    private void openSimOrEsimSettings() {
        Intent[] candidates = new Intent[] {
                new Intent(Settings.ACTION_MANAGE_ALL_SIM_PROFILES_SETTINGS),
                new Intent("android.settings.MANAGE_ALL_SIM_PROFILES_SETTINGS"),
                new Intent("com.samsung.settings.SIM_CARD_MANAGER_SETTINGS"),
                new Intent(Settings.ACTION_NETWORK_OPERATOR_SETTINGS),
                new Intent(Settings.ACTION_WIRELESS_SETTINGS)
        };
        openFirstAvailable(candidates, "SIM/eSIM settings are not exposed on this firmware or this device has no cellular/eSIM hardware.");
    }

    private void openTetheringSettings() {
        Intent[] candidates = new Intent[] {
                new Intent(Settings.ACTION_TETHER_SETTINGS),
                new Intent("android.settings.TETHER_SETTINGS"),
                new Intent(Settings.ACTION_WIRELESS_SETTINGS)
        };
        openFirstAvailable(candidates, "Hotspot/tethering settings are not exposed on this firmware.");
    }

    private void open(String action) {
        openFirstAvailable(new Intent[] { new Intent(action), new Intent(Settings.ACTION_SETTINGS) }, "Settings page is not available on this device.");
    }

    private void openAppSettings() {
        Intent intent = new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS);
        intent.setData(Uri.parse("package:" + getPackageName()));
        openFirstAvailable(new Intent[] { intent, new Intent(Settings.ACTION_SETTINGS) }, "Unable to open app settings.");
    }

    private void openFirstAvailable(Intent[] intents, String failureMessage) {
        for (Intent intent : intents) {
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            if (intent.resolveActivity(getPackageManager()) != null) {
                try {
                    startActivity(intent);
                    return;
                } catch (ActivityNotFoundException ignored) {
                    // Try the next fallback.
                } catch (SecurityException securityException) {
                    showMessage("Blocked by Android", "Android blocked this Settings page for third-party apps: " + securityException.getMessage());
                    return;
                }
            }
        }
        Toast.makeText(this, failureMessage, Toast.LENGTH_LONG).show();
        showMessage("Settings page unavailable", failureMessage + "\n\nOn a Galaxy Tab S9 FE+ Wi‑Fi tablet, cellular, SIM Manager, APN, roaming, and eSIM menus can be missing because the device does not include cellular hardware.");
    }

    private void addButton(LinearLayout root, String label, Runnable action) {
        Button button = new Button(this);
        button.setAllCaps(false);
        button.setText(label);
        button.setGravity(Gravity.CENTER);
        button.setOnClickListener(view -> action.run());
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        params.setMargins(0, dp(6), 0, dp(6));
        root.addView(button, params);
    }

    private TextView text(String value, int sp, boolean bold) {
        TextView textView = new TextView(this);
        textView.setText(value);
        textView.setTextSize(sp);
        textView.setLineSpacing(0, 1.12f);
        textView.setPadding(0, dp(6), 0, dp(6));
        if (bold) {
            textView.setTypeface(textView.getTypeface(), android.graphics.Typeface.BOLD);
        }
        return textView;
    }

    private void showMessage(String title, String message) {
        new AlertDialog.Builder(this)
                .setTitle(title)
                .setMessage(message)
                .setPositiveButton(android.R.string.ok, null)
                .show();
    }

    private String yesNo(boolean value) {
        return value ? "yes" : "no";
    }

    private String blankToUnknown(String value) {
        return value == null || value.trim().isEmpty() ? "Unknown / not connected" : value;
    }

    private int dp(int value) {
        return (int) (value * getResources().getDisplayMetrics().density + 0.5f);
    }
}
