#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$HOME/.local/share/cachy-caffeine"
BIN_DIR="$HOME/.local/bin"
AUTOSTART_DIR="$HOME/.config/autostart"
APPS_DIR="$HOME/.local/share/applications"

mkdir -p "$DATA_DIR/icons" "$BIN_DIR" "$AUTOSTART_DIR" "$APPS_DIR"

cp "$SCRIPT_DIR/cachy_caffeine.py" "$DATA_DIR/"
cp "$SCRIPT_DIR/icons/"*.svg "$DATA_DIR/icons/"

cat > "$BIN_DIR/cachy-caffeine" <<EOF
#!/bin/bash
exec python3 "$DATA_DIR/cachy_caffeine.py"
EOF
chmod +x "$BIN_DIR/cachy-caffeine"

# Icon= with an absolute path skips icon-theme lookup entirely (avoids the
# hicolor cache mess we hit with caffeine-ng).
sed -e "s|Exec=cachy-caffeine|Exec=$BIN_DIR/cachy-caffeine|" \
    -e "s|Icon=caffeine-cup-empty|Icon=$DATA_DIR/icons/caffeine-cup-empty.svg|" \
  "$SCRIPT_DIR/cachy-caffeine.desktop" > "$AUTOSTART_DIR/cachy-caffeine.desktop"

cp "$AUTOSTART_DIR/cachy-caffeine.desktop" "$APPS_DIR/cachy-caffeine.desktop"

update-desktop-database "$APPS_DIR" 2>/dev/null || true

echo "Installed. Run 'cachy-caffeine', find 'Cachy Caffeine' in your app menu, or log out and back in for autostart to take effect."
