#!/usr/bin/env python3
# PDF OCR to Markdown
# Copyright (C) 2026 A.T.Grep
# Licensed under the GNU Affero General Public License v3.0. See LICENSE.
"""
build_exe.py - Builds PDF OCR to Markdown on Windows or Linux.

Usage (with the project's virtual environment Python):
    python build_exe.py              Download language data (if missing) and build the app
    python build_exe.py --data-only  Download language data only (needed to run from source)
    python build_exe.py --package    Build, then create a ready-to-share release archive

Output:
    Windows: dist/PDF-OCR.exe    and  release/PDF-OCR-v<version>-Windows.zip
    Linux:   dist/PDF-OCR        and  release/PDF-OCR-v<version>-Linux.tar.gz
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TESSDATA = ROOT / "tessdata"
LANGS = ["eng", "ara"]
APP_SCRIPT = "pdf_ocr_standalone.py"
APP_NAME = "PDF-OCR"
ICON = "app_icon.png"
DATA_URL = "https://raw.githubusercontent.com/tesseract-ocr/tessdata_best/main/{}.traineddata"
# Used in the release guide when not building on GitHub; GitHub builds fill in the real link.
SOURCE_URL = "https://github.com/<your-username>/pdf-ocr-to-markdown"
IS_WINDOWS = os.name == "nt"
PLATFORM = "Windows" if IS_WINDOWS else "Linux"
EXECUTABLE = ROOT / "dist" / (f"{APP_NAME}.exe" if IS_WINDOWS else APP_NAME)


def step(message: str) -> None:
    print(f"\n=== {message} ===", flush=True)


def app_version() -> str:
    text = (ROOT / APP_SCRIPT).read_text(encoding="utf-8")
    match = re.search(r'^APP_VERSION\s*=\s*"([^"]+)"', text, re.MULTILINE)
    return match.group(1) if match else "0.0.0"


def check_packages() -> None:
    step("Checking packages")
    missing = []
    for module in ("pymupdf", "pymupdf4llm", "PyInstaller", "PIL"):
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    if missing:
        sys.exit(f"Missing packages: {', '.join(missing)}\n"
                 "Run the VS Code task '2. Install packages' first.\n"
                 "(PIL is provided by the 'pillow' package and converts the icon for Windows.)")
    print("All packages installed.")


def download_tessdata() -> None:
    step("Language data")
    TESSDATA.mkdir(exist_ok=True)
    for lang in LANGS:
        target = TESSDATA / f"{lang}.traineddata"
        if target.exists() and target.stat().st_size > 100_000:
            print(f"{target.name}: already present")
            continue
        url = DATA_URL.format(lang)
        print(f"{target.name}: downloading from {url}")
        temp = target.with_suffix(".part")
        try:
            urllib.request.urlretrieve(url, temp)
            temp.replace(target)
        except Exception as exc:
            temp.unlink(missing_ok=True)
            sys.exit(f"\nDownload failed: {exc}\n"
                     f"Download the file manually in your browser:\n  {url}\n"
                     f"Save it as:\n  {target}\nThen run this script again.")


def build() -> None:
    step(f"Building {APP_NAME} for {PLATFORM} (this takes a few minutes)")
    separator = ";" if IS_WINDOWS else ":"
    command = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--clean", "--onefile", "--windowed",
        "--name", APP_NAME,
        "--add-data", f"tessdata{separator}tessdata",
        "--collect-all", "pymupdf",
        "--collect-all", "pymupdf4llm",
        "--collect-all", "onnxruntime",
    ]
    try:
        __import__("pymupdf_layout")
        command += ["--collect-all", "pymupdf_layout"]
    except ImportError:
        pass
    icon = ROOT / ICON
    if icon.exists():
        command += ["--add-data", f"{ICON}{separator}."]
        if IS_WINDOWS:
            command += ["--icon", str(icon)]  # an embedded file icon is a Windows feature
        print(f"Icon: {ICON}")
    else:
        print(f"Icon: {ICON} not found; building without a custom icon.")
    command.append(APP_SCRIPT)
    if subprocess.run(command, cwd=ROOT).returncode != 0:
        sys.exit("\nBuild failed. Review the messages above.")
    print(f"\nBuild complete: {EXECUTABLE}")


def package() -> Path:
    version = app_version()
    step(f"Packaging release v{version} for {PLATFORM}")
    if not EXECUTABLE.exists():
        sys.exit(f"{EXECUTABLE} not found. Build the app first.")
    name = f"{APP_NAME}-v{version}-{PLATFORM}"
    release_dir = ROOT / "release"
    staging = release_dir / name
    shutil.rmtree(staging, ignore_errors=True)
    staging.mkdir(parents=True)

    shutil.copy2(EXECUTABLE, staging / EXECUTABLE.name)
    for document in ("LICENSE", "THIRD_PARTY_NOTICES.md"):
        if (ROOT / document).exists():
            shutil.copy2(ROOT / document, staging / document)
    if not IS_WINDOWS:
        for extra in (ICON, "install_linux.sh"):
            if (ROOT / extra).exists():
                shutil.copy2(ROOT / extra, staging / extra)
        for runnable in (APP_NAME, "install_linux.sh"):
            if (staging / runnable).exists():
                (staging / runnable).chmod(0o755)

    guide = ROOT / "READ_ME_FIRST.txt"
    if guide.exists():
        repository = os.environ.get("GITHUB_REPOSITORY")
        source_url = f"https://github.com/{repository}" if repository else SOURCE_URL
        text = guide.read_text(encoding="utf-8")
        text = text.replace("{{VERSION}}", version).replace("{{SOURCE_URL}}", source_url)
        newline = "\r\n" if IS_WINDOWS else "\n"
        with open(staging / guide.name, "w", encoding="utf-8", newline=newline) as handle:
            handle.write(text)

    archive_format = "zip" if IS_WINDOWS else "gztar"
    archive = shutil.make_archive(str(release_dir / name), archive_format, root_dir=release_dir, base_dir=name)
    shutil.rmtree(staging)
    print(f"Release archive: {archive}")
    return Path(archive)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build PDF OCR to Markdown.")
    parser.add_argument("--data-only", action="store_true", help="Download the OCR language data only")
    parser.add_argument("--package", action="store_true", help="Build, then create a release archive")
    args = parser.parse_args()

    if args.data_only:
        download_tessdata()
        return
    check_packages()
    download_tessdata()
    build()
    if args.package:
        package()


if __name__ == "__main__":
    main()
