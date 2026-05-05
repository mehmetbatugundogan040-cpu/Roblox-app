"""Turkey Radio desktop app.

Run in VS Code terminal:
    python src/turkey_radio_app.py
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any

import requests
import vlc

API_URL = "https://de1.api.radio-browser.info/json/stations/search"
DEFAULT_CITIES = [
    "Istanbul",
    "Mersin",
    "Adana",
    "Gaziantep",
    "Alanya",
    "Antalya",
    "Canakkale",
    "Balikesir",
]


class TurkeyRadioApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Turkey Radio App - All Turkish Channels")
        self.root.geometry("860x620")
        self.root.configure(bg="#0B1220")

        self.instance = vlc.Instance("--no-video")
        self.player = self.instance.media_player_new()
        self.current_url = ""
        self.all_stations: list[dict[str, Any]] = []

        title = tk.Label(
            root,
            text="🇹🇷 Turkey Radio Explorer",
            font=("Segoe UI", 21, "bold"),
            fg="#F8FAFC",
            bg="#0B1220",
        )
        title.pack(pady=(12, 4))

        self.status_var = tk.StringVar(value="Loading Turkish stations... (No in-app ads)")
        status = tk.Label(
            root,
            textvariable=self.status_var,
            font=("Segoe UI", 10),
            fg="#93C5FD",
            bg="#0B1220",
        )
        status.pack(pady=(0, 10))

        top_controls = tk.Frame(root, bg="#0B1220")
        top_controls.pack(fill="x", padx=14)

        tk.Label(top_controls, text="Search:", fg="#E2E8F0", bg="#0B1220").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh_list())
        tk.Entry(top_controls, textvariable=self.search_var, width=30).pack(side="left", padx=(6, 10))

        tk.Label(top_controls, text="City:", fg="#E2E8F0", bg="#0B1220").pack(side="left")
        self.city_var = tk.StringVar(value="All")
        self.city_combo = ttk.Combobox(top_controls, textvariable=self.city_var, state="readonly", width=24)
        self.city_combo.pack(side="left", padx=(6, 10))
        self.city_combo.bind("<<ComboboxSelected>>", lambda _e: self.refresh_list())

        tk.Button(
            top_controls,
            text="Reload from Internet",
            command=self.load_stations,
            bg="#1D4ED8",
            fg="#FFFFFF",
            relief="flat",
            padx=8,
            pady=4,
        ).pack(side="left")

        mid = tk.Frame(root, bg="#0B1220")
        mid.pack(fill="both", expand=True, padx=14, pady=10)

        self.station_list = tk.Listbox(
            mid,
            bg="#111827",
            fg="#F9FAFB",
            selectbackground="#2563EB",
            font=("Segoe UI", 10),
            activestyle="none",
        )
        self.station_list.pack(side="left", fill="both", expand=True)
        self.station_list.bind("<Double-Button-1>", lambda _e: self.play_selected())

        scroll = tk.Scrollbar(mid, command=self.station_list.yview)
        scroll.pack(side="right", fill="y")
        self.station_list.config(yscrollcommand=scroll.set)

        bottom = tk.Frame(root, bg="#0B1220")
        bottom.pack(fill="x", padx=14, pady=(0, 14))

        tk.Button(bottom, text="Play Selected", command=self.play_selected, bg="#16A34A", fg="white", relief="flat", padx=10, pady=6).pack(side="left")
        tk.Button(bottom, text="Stop", command=self.stop, bg="#B91C1C", fg="white", relief="flat", padx=10, pady=6).pack(side="left", padx=8)
        tk.Button(bottom, text="Replay", command=self.replay, bg="#2563EB", fg="white", relief="flat", padx=10, pady=6).pack(side="left")

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.load_stations()

    def load_stations(self) -> None:
        self.status_var.set("Loading all Turkish stations from internet directory...")
        self.root.update_idletasks()
        try:
            params = {
                "countrycode": "TR",
                "hidebroken": "true",
                "order": "name",
                "reverse": "false",
                "limit": "10000",
            }
            response = requests.get(API_URL, params=params, timeout=20)
            response.raise_for_status()
            stations = response.json()
        except Exception as exc:
            messagebox.showerror("Load Error", f"Could not load station list.\n\n{exc}")
            self.status_var.set("Failed to load stations")
            return

        filtered: list[dict[str, Any]] = []
        for s in stations:
            name = (s.get("name") or "").strip()
            url = (s.get("url_resolved") or s.get("url") or "").strip()
            if not name or not url:
                continue
            filtered.append({
                "name": name,
                "city": (s.get("state") or s.get("tags") or "Unknown").strip(),
                "url": url,
                "codec": s.get("codec") or "",
                "bitrate": s.get("bitrate") or 0,
            })

        self.all_stations = filtered
        self.populate_city_filter()
        self.refresh_list()
        self.status_var.set(f"Loaded {len(self.all_stations)} Turkish stations")

    def populate_city_filter(self) -> None:
        cities = sorted({st["city"] for st in self.all_stations if st["city"] and st["city"] != "Unknown"})

        ordered = ["All"]
        for city in DEFAULT_CITIES:
            if city in cities:
                ordered.append(city)
        for city in cities:
            if city not in ordered:
                ordered.append(city)

        self.city_combo["values"] = ordered
        if self.city_var.get() not in ordered:
            self.city_var.set("All")

    def refresh_list(self) -> None:
        query = self.search_var.get().strip().lower()
        city = self.city_var.get().strip()

        self.station_list.delete(0, tk.END)
        self.view_items: list[dict[str, Any]] = []

        for station in self.all_stations:
            text = station["name"].lower()
            city_text = station["city"].lower()
            if query and query not in text and query not in city_text:
                continue
            if city != "All" and station["city"] != city:
                continue
            label = f"{station['name']}  |  {station['city']}  |  {station['codec']} {station['bitrate']}kbps"
            self.station_list.insert(tk.END, label)
            self.view_items.append(station)

        self.status_var.set(f"Showing {len(self.view_items)} stations")

    def play_selected(self) -> None:
        selected = self.station_list.curselection()
        if not selected:
            self.status_var.set("Select a station first")
            return

        station = self.view_items[selected[0]]
        self.current_url = station["url"]
        media = self.instance.media_new(self.current_url)
        self.player.set_media(media)
        result = self.player.play()

        if result == -1:
            messagebox.showerror("Playback Error", f"Could not start {station['name']}.")
            self.status_var.set("Playback failed")
            return

        self.status_var.set(f"Now playing: {station['name']} ({station['city']})")

    def stop(self) -> None:
        self.player.stop()
        self.status_var.set("Stopped")

    def replay(self) -> None:
        if not self.current_url:
            self.status_var.set("Pick a station first")
            return
        media = self.instance.media_new(self.current_url)
        self.player.set_media(media)
        self.player.play()
        self.status_var.set("Replaying current station")

    def on_close(self) -> None:
        self.player.stop()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    TurkeyRadioApp(root)
    root.mainloop()
