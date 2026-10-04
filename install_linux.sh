#!/usr/bin/env bash
# PDF OCR to Markdown - Linux installer
# Copyright (C) 2026 A.T.Grep
# Licensed under the GNU Affero General Public License v3.0. See LICENSE.
#
# Installs the app for the current user (no sudo needed) and adds it to the applications menu.
#   ./install_linux.sh             install or update
#   ./install_linux.sh --uninstall remove

set -euo pipefail

APP_ID="pdf-ocr-to-markdown"
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
    rm -f "$BIN_DIR/pdf-ocr" "$DESKTOP_FILE" "$ICON_FILE"
    refresh_menu
    echo "PDF OCR to Markdown was removed."
    exit 0
fi

if [[ ! -f "$SOURCE_DIR/PDF-OCR" ]]; then
    echo "PDF-OCR was not found next to this script."
    echo "Run the script from the extracted release folder."
    exit 1
fi

mkdir -p "$APP_DIR" "$BIN_DIR" "$(dirname "$DESKTOP_FILE")" "$(dirname "$ICON_FILE")"
install -m 755 "$SOURCE_DIR/PDF-OCR" "$APP_DIR/PDF-OCR"
for document in LICENSE THIRD_PARTY_NOTICES.md READ_ME_FIRST.txt; do
    if [[ -f "$SOURCE_DIR/$document" ]]; then
        install -m 644 "$SOURCE_DIR/$document" "$APP_DIR/$document"
    fi
done
if [[ -f "$SOURCE_DIR/app_icon.png" ]]; then
    install -m 644 "$SOURCE_DIR/app_icon.png" "$ICON_FILE"
fi
ln -sf "$APP_DIR/PDF-OCR" "$BIN_DIR/pdf-ocr"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=PDF OCR to Markdown
Comment=Turn scanned PDFs into searchable PDFs and Markdown
Exec="$APP_DIR/PDF-OCR"
Icon=$APP_ID
Terminal=false
Categories=Office;Utility;
Keywords=PDF;OCR;Markdown;scan;Arabic;
StartupWMClass=Pdf-ocr
EOF
chmod 644 "$DESKTOP_FILE"
refresh_menu

echo "PDF OCR to Markdown is installed."
echo "Open it from the applications menu, or run: pdf-ocr"
echo "To remove it later, run: $SOURCE_DIR/install_linux.sh --uninstall"
