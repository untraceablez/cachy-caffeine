#!/usr/bin/env python3
"""Cachy Caffeine: keeps the system awake, toggled from the tray."""
import os
import signal
import subprocess
import time

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("AyatanaAppIndicator3", "0.1")
from gi.repository import AyatanaAppIndicator3 as AppIndicator3
from gi.repository import GLib, Gtk

APP_ID = "cachy-caffeine"
ICON_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
ICON_FULL = "caffeine-cup-full"
ICON_EMPTY = "caffeine-cup-empty"
TIMER_PRESET_MINUTES = (5, 10, 15, 30, 60)


class CachyCaffeine:
    def __init__(self):
        self.inhibit_proc = None
        self.timer_id = None
        self.deadline = None

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

        timer_submenu = Gtk.Menu()
        for minutes in TIMER_PRESET_MINUTES:
            item = Gtk.MenuItem(label=f"{minutes} minutes")
            item.connect("activate", self.on_timer_preset, minutes * 60)
            timer_submenu.append(item)
        timer_submenu.append(Gtk.SeparatorMenuItem())
        custom_item = Gtk.MenuItem(label="Custom...")
        custom_item.connect("activate", self.on_timer_custom)
        timer_submenu.append(custom_item)

        timer_item = Gtk.MenuItem(label="Timer")
        timer_item.set_submenu(timer_submenu)
        self.menu.append(timer_item)

        self.remaining_item = Gtk.MenuItem(label="")
        self.remaining_item.set_sensitive(False)
        self.menu.append(self.remaining_item)

        self.menu.append(Gtk.SeparatorMenuItem())

        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", self.on_quit)
        self.menu.append(quit_item)

        self.menu.show_all()
        self.remaining_item.hide()
        self.indicator.set_menu(self.menu)

        self.set_active(False)

    def on_toggle(self, _widget):
        self.set_active(self.inhibit_proc is None)

    def on_timer_preset(self, _widget, seconds):
        self.start_timer(seconds)

    def on_timer_custom(self, _widget):
        dialog = Gtk.Dialog(title="Custom timer", flags=Gtk.DialogFlags.MODAL)
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Start", Gtk.ResponseType.OK)
        dialog.set_default_response(Gtk.ResponseType.OK)

        box = Gtk.Box(spacing=6, margin=12)
        spins = []
        for label in ("hours", "minutes", "seconds"):
            spin = Gtk.SpinButton.new_with_range(0, 99, 1)
            spin.set_max_length(2)
            spin.set_width_chars(2)
            spin.set_numeric(True)
            spin.set_activates_default(True)
            spins.append(spin)
            box.pack_start(spin, False, False, 0)
            box.pack_start(Gtk.Label(label=label), False, False, 0)
        dialog.get_content_area().add(box)
        dialog.show_all()

        response = dialog.run()
        hours, minutes, seconds = (spin.get_value_as_int() for spin in spins)
        dialog.destroy()

        total = hours * 3600 + minutes * 60 + seconds
        if response == Gtk.ResponseType.OK and total > 0:
            self.start_timer(total)

    def start_timer(self, seconds: int):
        self.set_active(True)
        self.cancel_timer()
        self.deadline = time.monotonic() + seconds
        self.timer_id = GLib.timeout_add_seconds(1, self.on_timer_tick)
        self.update_remaining()

    def cancel_timer(self):
        if self.timer_id is not None:
            GLib.source_remove(self.timer_id)
        self.timer_id = None
        self.deadline = None
        self.remaining_item.hide()

    def on_timer_tick(self):
        if time.monotonic() >= self.deadline:
            self.timer_id = None  # source is removed by returning False
            self.set_active(False)
            return False
        self.update_remaining()
        return True

    def update_remaining(self):
        left = max(0, round(self.deadline - time.monotonic()))
        hours, rest = divmod(left, 3600)
        minutes, seconds = divmod(rest, 60)
        self.remaining_item.set_label(f"Time left: {hours:d}:{minutes:02d}:{seconds:02d}")
        self.remaining_item.show()

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

        if not active:
            self.cancel_timer()

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
