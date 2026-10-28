#!/usr/bin/env python3
"""Cachy Caffeine: keeps the system awake, toggled from the tray."""
import os
import signal
import subprocess

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("AyatanaAppIndicator3", "0.1")
from gi.repository import AyatanaAppIndicator3 as AppIndicator3
from gi.repository import Gtk

APP_ID = "cachy-caffeine"
ICON_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
ICON_FULL = "caffeine-cup-full"
ICON_EMPTY = "caffeine-cup-empty"


class CachyCaffeine:
    def __init__(self):
        self.inhibit_proc = None

        self.indicator = AppIndicator3.Indicator.new(
            APP_ID, ICON_EMPTY, AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_icon_theme_path(ICON_DIR)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_title("Cachy Caffeine")

        self.menu = Gtk.Menu()

        self.toggle_item = Gtk.MenuItem(label="Enable caffeine")
        self.toggle_item.connect("activate", self.on_toggle)
        self.menu.append(self.toggle_item)

        self.menu.append(Gtk.SeparatorMenuItem())

        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", self.on_quit)
        self.menu.append(quit_item)

        self.menu.show_all()
        self.indicator.set_menu(self.menu)

        self.set_active(False)

    def on_toggle(self, _widget):
        self.set_active(self.inhibit_proc is None)

    def set_active(self, active: bool):
        if active and self.inhibit_proc is None:
            self.inhibit_proc = subprocess.Popen(
                [
                    "systemd-inhibit",
                    "--what=idle:sleep",
                    f"--who={APP_ID}",
                    "--why=Manual caffeine mode",
                    "sleep",
                    "infinity",
                ]
            )
        elif not active and self.inhibit_proc is not None:
            self.inhibit_proc.terminate()
            try:
                self.inhibit_proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.inhibit_proc.kill()
            self.inhibit_proc = None

        icon_name = ICON_FULL if active else ICON_EMPTY
        # set_icon_full() reliably emits the NewIcon signal on AyatanaAppIndicator;
        # caffeine-ng's older bound API sometimes skipped it, leaving the tray stale.
        self.indicator.set_icon_full(icon_name, "Caffeine active" if active else "Caffeine inactive")

        self.toggle_item.set_label("Disable caffeine" if active else "Enable caffeine")
        self.indicator.set_title(
            "Cachy Caffeine - active" if active else "Cachy Caffeine - inactive"
        )

    def on_quit(self, _widget):
        self.set_active(False)
        Gtk.main_quit()


def main():
    # Avoid orphaning the inhibit subprocess if we get killed abruptly.
    signal.signal(signal.SIGTERM, lambda *_: Gtk.main_quit())
    app = CachyCaffeine()
    try:
        Gtk.main()
    finally:
        app.set_active(False)


if __name__ == "__main__":
    main()
