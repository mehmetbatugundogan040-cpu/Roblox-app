"""Samsung Galaxy eSIM and cellular settings helper.

Run in VS Code terminal:
    python src/samsung_esim_settings_app.py
"""

from __future__ import annotations

import platform
import subprocess
import tkinter as tk
from dataclasses import dataclass
from tkinter import messagebox, ttk

APP_TITLE = "Samsung Galaxy eSIM Settings Helper"
ADB_PACKAGE = "com.android.settings"


@dataclass(frozen=True)
class SettingsShortcut:
    """A Samsung/Android Settings destination that can be opened with ADB."""

    name: str
    action: str
    description: str

    @property
    def adb_command(self) -> str:
        return f"adb shell am start -a {self.action}"


SHORTCUTS = [
    SettingsShortcut(
        "Mobile network settings",
        "android.settings.WIRELESS_SETTINGS",
        "Opens the wireless/network area that contains Mobile networks on cellular Galaxy devices.",
    ),
    SettingsShortcut(
        "SIM card manager / eSIM area",
        "android.settings.NETWORK_OPERATOR_SETTINGS",
        "Opens the carrier/operator area when the device firmware exposes SIM or eSIM management.",
    ),
    SettingsShortcut(
        "Data usage",
        "android.settings.DATA_USAGE_SETTINGS",
        "Opens Android data usage controls for cellular/Wi-Fi metering and limits.",
    ),
    SettingsShortcut(
        "Wi-Fi settings",
        "android.settings.WIFI_SETTINGS",
        "Opens Wi-Fi settings for Wi-Fi-only tablets and phones.",
    ),
    SettingsShortcut(
        "VPN settings",
        "android.settings.VPN_SETTINGS",
        "Opens VPN settings for carrier-style private-network or hotspot workflows.",
    ),
    SettingsShortcut(
        "Airplane mode radios",
        "android.settings.AIRPLANE_MODE_SETTINGS",
        "Opens airplane-mode/radio controls exposed by the device build.",
    ),
]

CAPABILITY_ROWS = [
    (
        "Galaxy phone or tablet with cellular modem",
        "Physical SIM, eSIM, mobile data, calls, SMS, carrier provisioning, APN settings, roaming settings.",
    ),
    (
        "Galaxy Tab S9 FE+ Wi-Fi / non-cellular Galaxy tablet",
        "Wi-Fi, Bluetooth, VPN, hotspot client, Wi-Fi calling helper apps only when paired; no built-in SIM/eSIM/mobile data hardware.",
    ),
    (
        "External hotspot or tethered phone",
        "Uses another device's cellular connection over Wi-Fi, Bluetooth, or USB; the tablet still does not become an eSIM device.",
    ),
]

GUIDE_STEPS = [
    "Open Samsung Settings > Connections.",
    "If the hardware supports cellular, open SIM manager or Mobile networks and choose Add eSIM / Add mobile plan.",
    "Scan the carrier QR code or enter the activation code supplied by the carrier.",
    "Choose default SIM/eSIM for mobile data, calls, and text messages when those options exist.",
    "For Wi-Fi-only Galaxy tablets, use Wi-Fi, VPN, a phone hotspot, or USB tethering instead of eSIM provisioning.",
]


class SamsungEsimSettingsApp:
    """Desktop helper for Samsung Galaxy mobile-network Settings workflows."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("980x700")
        self.root.minsize(850, 620)
        self.root.configure(bg="#0F172A")

        self.selected_shortcut = tk.StringVar(value=SHORTCUTS[0].name)
        self.status_var = tk.StringVar(value="Ready. Connect a Galaxy device with USB debugging to launch Settings shortcuts.")
        self.device_profile = tk.StringVar(value="Samsung Galaxy Tab S9 FE+ Wi-Fi / non-cellular")

        self._build_header()
        self._build_tabs()
        self._build_status_bar()

    def _build_header(self) -> None:
        header = tk.Frame(self.root, bg="#0F172A")
        header.pack(fill="x", padx=18, pady=(16, 10))

        tk.Label(
            header,
            text="📶 Samsung Galaxy eSIM + Mobile Settings Helper",
            font=("Segoe UI", 21, "bold"),
            fg="#F8FAFC",
            bg="#0F172A",
        ).pack(anchor="w")
        tk.Label(
            header,
            text=(
                "A safe service-style launcher and guide for Samsung Settings, SIM manager, "
                "mobile networks, VPN, Wi‑Fi, and non-cellular Galaxy tablets."
            ),
            font=("Segoe UI", 10),
            fg="#BFDBFE",
            bg="#0F172A",
            wraplength=920,
            justify="left",
        ).pack(anchor="w", pady=(5, 0))

    def _build_tabs(self) -> None:
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=18, pady=(0, 10))

        self.actions_text = self._create_text_tab(notebook, "Settings launcher")
        self.guide_text = self._create_text_tab(notebook, "Samsung guide")
        self.matrix_text = self._create_text_tab(notebook, "Capabilities")
        self.service_text = self._create_text_tab(notebook, "Service checklist")

        self._populate_actions_tab()
        self._populate_guide_tab()
        self._populate_matrix_tab()
        self._populate_service_tab()

    def _create_text_tab(self, notebook: ttk.Notebook, label: str) -> tk.Frame:
        frame = tk.Frame(notebook, bg="#111827")
        notebook.add(frame, text=label)
        return frame

    def _populate_actions_tab(self) -> None:
        frame = self.actions_text

        top = tk.Frame(frame, bg="#111827")
        top.pack(fill="x", padx=16, pady=16)

        tk.Label(top, text="Device profile:", fg="#E5E7EB", bg="#111827", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Combobox(
            top,
            textvariable=self.device_profile,
            values=[
                "Samsung Galaxy Tab S9 FE+ Wi-Fi / non-cellular",
                "Samsung Galaxy cellular tablet",
                "Samsung Galaxy phone",
                "Other Android device",
            ],
            state="readonly",
            width=46,
        ).grid(row=0, column=1, sticky="we", padx=(10, 0))

        tk.Label(top, text="Settings shortcut:", fg="#E5E7EB", bg="#111827", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=(12, 0))
        shortcut_box = ttk.Combobox(
            top,
            textvariable=self.selected_shortcut,
            values=[shortcut.name for shortcut in SHORTCUTS],
            state="readonly",
            width=46,
        )
        shortcut_box.grid(row=1, column=1, sticky="we", padx=(10, 0), pady=(12, 0))
        shortcut_box.bind("<<ComboboxSelected>>", lambda _event: self.update_command_preview())
        top.columnconfigure(1, weight=1)

        buttons = tk.Frame(frame, bg="#111827")
        buttons.pack(fill="x", padx=16, pady=(0, 12))
        tk.Button(buttons, text="Copy ADB command", command=self.copy_adb_command, bg="#2563EB", fg="white", relief="flat", padx=10, pady=7).pack(side="left")
        tk.Button(buttons, text="Run ADB command", command=self.run_adb_command, bg="#16A34A", fg="white", relief="flat", padx=10, pady=7).pack(side="left", padx=8)
        tk.Button(buttons, text="Check ADB devices", command=self.check_adb_devices, bg="#7C3AED", fg="white", relief="flat", padx=10, pady=7).pack(side="left")

        self.command_preview = tk.Text(frame, height=15, bg="#020617", fg="#E2E8F0", insertbackground="#E2E8F0", wrap="word", font=("Consolas", 10))
        self.command_preview.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.update_command_preview()

    def _populate_guide_tab(self) -> None:
        text = self._make_readonly_text(self.guide_text)
        text.insert("end", "Samsung eSIM / SIM / mobile cellular Settings guide\n", "title")
        text.insert("end", "\n")
        for number, step in enumerate(GUIDE_STEPS, start=1):
            text.insert("end", f"{number}. {step}\n")
        text.insert("end", "\nImportant limitation for Wi‑Fi Galaxy devices\n", "section")
        text.insert(
            "end",
            (
                "A Wi‑Fi-only Galaxy tablet, including a Galaxy Tab S9 FE+ Wi‑Fi model, does not include the cellular modem, "
                "SIM slot/eUICC, antennas, carrier firmware, or IMEI provisioning required for real mobile data or eSIM activation. "
                "This helper can open available Settings screens and show the right workflow, but it cannot create cellular hardware in software.\n"
            ),
        )
        text.configure(state="disabled")

    def _populate_matrix_tab(self) -> None:
        text = self._make_readonly_text(self.matrix_text)
        text.insert("end", "Galaxy device capability matrix\n\n", "title")
        for device_type, abilities in CAPABILITY_ROWS:
            text.insert("end", f"• {device_type}\n", "section")
            text.insert("end", f"  {abilities}\n\n")
        text.configure(state="disabled")

    def _populate_service_tab(self) -> None:
        text = self._make_readonly_text(self.service_text)
        text.insert("end", "Service app checklist for Samsung Galaxy devices\n\n", "title")
        checklist = [
            "Enable Developer options on the Galaxy device.",
            "Enable USB debugging and connect the device to this computer.",
            "Install Android Platform Tools so the adb command is available.",
            "Use Settings launcher to open Samsung/Android network Settings screens.",
            "On non-cellular tablets, configure Wi‑Fi, VPN, Bluetooth tethering, USB tethering, or a phone hotspot.",
            "On cellular models, use SIM manager and Mobile networks for eSIM activation, APN, roaming, data limits, and defaults.",
        ]
        for item in checklist:
            text.insert("end", f"☐ {item}\n")
        text.insert("end", "\nGenerated local diagnostics\n", "section")
        text.insert("end", self._local_diagnostics())
        text.configure(state="disabled")

    def _make_readonly_text(self, frame: tk.Frame) -> tk.Text:
        text = tk.Text(frame, bg="#020617", fg="#E5E7EB", insertbackground="#E5E7EB", wrap="word", font=("Segoe UI", 11), padx=14, pady=14)
        text.tag_configure("title", foreground="#93C5FD", font=("Segoe UI", 16, "bold"))
        text.tag_configure("section", foreground="#FBBF24", font=("Segoe UI", 12, "bold"))
        text.pack(fill="both", expand=True, padx=16, pady=16)
        return text

    def _build_status_bar(self) -> None:
        tk.Label(
            self.root,
            textvariable=self.status_var,
            anchor="w",
            font=("Segoe UI", 9),
            fg="#CBD5E1",
            bg="#1E293B",
            padx=12,
            pady=6,
        ).pack(fill="x", side="bottom")

    def selected_settings_shortcut(self) -> SettingsShortcut:
        selected_name = self.selected_shortcut.get()
        return next(shortcut for shortcut in SHORTCUTS if shortcut.name == selected_name)

    def update_command_preview(self) -> None:
        shortcut = self.selected_settings_shortcut()
        profile = self.device_profile.get()
        warning = ""
        if "non-cellular" in profile:
            warning = (
                "\nNote: this profile is Wi‑Fi-only. Samsung may hide SIM manager, eSIM, APN, roaming, and "
                "mobile data toggles because the required cellular hardware is not present.\n"
            )

        preview = (
            f"Shortcut: {shortcut.name}\n"
            f"Description: {shortcut.description}\n\n"
            f"ADB command:\n{shortcut.adb_command}\n"
            f"\nPackage hint:\nadb shell monkey -p {ADB_PACKAGE} 1\n"
            f"{warning}\n"
            "If ADB reports that the activity cannot be resolved, that Settings screen is not exposed by this device/firmware."
        )
        self.command_preview.configure(state="normal")
        self.command_preview.delete("1.0", "end")
        self.command_preview.insert("end", preview)
        self.command_preview.configure(state="disabled")
        self.status_var.set(f"Selected: {shortcut.name}")

    def copy_adb_command(self) -> None:
        command = self.selected_settings_shortcut().adb_command
        self.root.clipboard_clear()
        self.root.clipboard_append(command)
        self.status_var.set(f"Copied: {command}")

    def run_adb_command(self) -> None:
        command = self.selected_settings_shortcut().adb_command.split()
        self._run_command(command, "ADB Settings launcher")

    def check_adb_devices(self) -> None:
        self._run_command(["adb", "devices", "-l"], "ADB device check")

    def _run_command(self, command: list[str], title: str) -> None:
        try:
            result = subprocess.run(command, check=False, capture_output=True, text=True, timeout=20)
        except FileNotFoundError:
            messagebox.showwarning(title, "adb was not found. Install Android Platform Tools and add it to PATH.")
            self.status_var.set("adb not found")
            return
        except subprocess.TimeoutExpired:
            messagebox.showwarning(title, "The adb command timed out after 20 seconds.")
            self.status_var.set("adb command timed out")
            return

        output = (result.stdout + result.stderr).strip() or "Command finished with no output."
        if result.returncode == 0:
            messagebox.showinfo(title, output)
            self.status_var.set(f"{title} finished")
        else:
            messagebox.showwarning(title, output)
            self.status_var.set(f"{title} failed with exit code {result.returncode}")

    def _local_diagnostics(self) -> str:
        return (
            f"Computer OS: {platform.system()} {platform.release()}\n"
            f"Python: {platform.python_version()}\n"
            "Required external tool for device control: adb from Android Platform Tools\n"
        )


def main() -> None:
    root = tk.Tk()
    SamsungEsimSettingsApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
