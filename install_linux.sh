#!/usr/bin/env bash
# GrepAll - Linux installer
# Copyright (C) 2026 A.T.Grep
# Licensed under the GNU Affero General Public License v3.0. See LICENSE.
#
# Installs the app for the current user (no sudo needed) and adds it to the applications menu.
#   ./install_linux.sh             install or update
#   ./install_linux.sh --uninstall remove

set -euo pipefail

APP_ID="grepall"
APP_DIR="$HOME/.local/share/$APP_ID"
BIN_DIR="$HOME/.local/bin"
DESKTOP_FILE="$HOME/.local/share/applications/$APP_ID.desktop"
ICON_FILE="$HOME/.local/share/icons/hicolor/256x256/apps/$APP_ID.png"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

refresh_menu() {
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database "$HOME/.local/share/applications" >/dev/null 2>&1 || true
    fi
    if command -v gtk-update-icon-cache >/dev/null 2>&1; then
        gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" >/dev/null 2>&1 || true
    fi
}

if [[ "${1:-}" == "--uninstall" ]]; then
    rm -rf "$APP_DIR"
    rm -f "$BIN_DIR/grepall" "$DESKTOP_FILE" "$ICON_FILE"
    refresh_menu
    echo "GrepAll was removed."
    exit 0
fi

if [[ ! -f "$SOURCE_DIR/GrepAll" || ! -d "$SOURCE_DIR/_internal" ]]; then
    echo "GrepAll and its _internal folder were not found next to this script."
    echo "Run the script from the extracted release folder."
    exit 1
fi

# Remove an installation from the versions named "PDF OCR to Markdown" (1.3), if present.
OLD_ID="pdf-ocr-to-markdown"
rm -rf "$HOME/.local/share/$OLD_ID"
rm -f "$BIN_DIR/pdf-ocr" "$HOME/.local/share/applications/$OLD_ID.desktop" \
      "$HOME/.local/share/icons/hicolor/256x256/apps/$OLD_ID.png"

rm -rf "$APP_DIR"  # replaces any previous version completely
mkdir -p "$APP_DIR" "$BIN_DIR" "$(dirname "$DESKTOP_FILE")" "$(dirname "$ICON_FILE")"
install -m 755 "$SOURCE_DIR/GrepAll" "$APP_DIR/GrepAll"
cp -a "$SOURCE_DIR/_internal" "$APP_DIR/_internal"
for document in LICENSE THIRD_PARTY_NOTICES.md READ_ME_FIRST.txt install_linux.sh; do
    if [[ -f "$SOURCE_DIR/$document" ]]; then
        install -m 644 "$SOURCE_DIR/$document" "$APP_DIR/$document"
    fi
done
if [[ -f "$SOURCE_DIR/app_icon.png" ]]; then
    install -m 644 "$SOURCE_DIR/app_icon.png" "$ICON_FILE"
fi
ln -sf "$APP_DIR/GrepAll" "$BIN_DIR/grepall"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=GrepAll
GenericName=OCR Tool
Comment=Offline OCR for PDFs and images, with Arabic support
Exec="$APP_DIR/GrepAll"
Icon=$APP_ID
Terminal=false
Categories=Office;Utility;
Keywords=PDF;OCR;Markdown;scan;image;Arabic;
StartupWMClass=Grepall
EOF
chmod 644 "$DESKTOP_FILE"
refresh_menu

echo "GrepAll is installed."
echo "Open it from the applications menu, or run: grepall"
echo "You can delete the extracted folder now."
echo "To remove the app later, run: bash ~/.local/share/$APP_ID/install_linux.sh --uninstall"
