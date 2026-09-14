#!/bin/bash
pkill -f cachy_caffeine.py 2>/dev/null

rm -rf "$HOME/.local/share/cachy-caffeine"
rm -f "$HOME/.local/bin/cachy-caffeine"
rm -f "$HOME/.config/autostart/cachy-caffeine.desktop"
rm -f "$HOME/.local/share/applications/cachy-caffeine.desktop"

echo "Desinstalado."
