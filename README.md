# cachy-caffeine

*[Leia em português](README-pt-br.md)*

A simple "caffeine mode" for Linux (built and tested on CachyOS/Arch + KDE Plasma),
like macOS's Caffeine: a tray icon that, when active, keeps the screen from locking
and the machine from suspending on its own due to inactivity.

Full steaming cup icon = active. Empty gray outline = inactive.

## How it works

- Tray icon via `AyatanaAppIndicator3` (GTK/PyGObject), pointed at this repo's own
  `icons/` folder (`set_icon_theme_path`) so it never depends on the system icon
  theme being able to resolve it
- Icon updates go through `set_icon_full()`, which reliably redraws the panel on
  every state change
- Toggling it on spawns a `systemd-inhibit --what=idle:sleep` in the background —
  that's the actual mechanism blocking suspend/lock, not this script itself
- Toggling it off (or closing the app) kills that process, restoring normal
  lock/suspend behavior; the same cleanup runs automatically if the app exits, so
  it never leaves an orphaned inhibitor running
- State is never persisted across reboots — it always starts inactive, by design
  (same as macOS's Caffeine)

## Dependencies

- Python 3
- PyGObject (`python-gobject` on Arch)
- `libayatana-appindicator` (or `libappindicator-gtk3` as a fallback)
- `systemd` (for `systemd-inhibit`)

```bash
sudo pacman -S python-gobject libayatana-appindicator
```

## Install

```bash
./install.sh
```

This copies the files to `~/.local/share/cachy-caffeine`, creates the
`cachy-caffeine` command in `~/.local/bin`, and registers autostart at
`~/.config/autostart/cachy-caffeine.desktop` (launches on every login), plus an
application menu entry.

## Uninstall

```bash
./uninstall.sh
```

## Usage

Click the tray icon to open the menu and choose "Ativar cafeine" / "Desativar
cafeine" (enable/disable caffeine — menu labels are currently in Portuguese).
