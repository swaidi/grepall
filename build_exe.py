#!/usr/bin/env python3
# GrepAll - Offline OCR for PDFs and images, with Arabic support
# Copyright (C) 2026 A.T.Grep
# Licensed under the GNU Affero General Public License v3.0. See LICENSE.
"""
build_exe.py - Builds GrepAll on Windows or Linux.

Usage (with the project's virtual environment Python):
    python build_exe.py              Download language data (if missing) and build the app
    python build_exe.py --data-only  Download language data only (needed to run from source)
    python build_exe.py --package    Build, then create the ready-to-share release files

Output (a folder build, which starts much faster than a single-file build):
    Windows: dist/GrepAll/GrepAll.exe, and in release/:
             GrepAll-v<version>-Windows-Setup.exe  (installer; needs Inno Setup 6 to build)
             GrepAll-v<version>-Windows.zip        (portable)
    Linux:   dist/GrepAll/GrepAll, and release/GrepAll-v<version>-Linux.tar.gz
The app needs the whole dist/GrepAll folder, including its _internal subfolder.

The Windows installer is built with Inno Setup 6 (free, https://jrsoftware.org/isinfo.php).
If it is not installed locally, the installer step is skipped and the portable ZIP is still created.
On GitHub, Inno Setup is installed automatically when missing.
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
APP_NAME = "GrepAll"
ICON = "app_icon.png"
DATA_URL = "https://raw.githubusercontent.com/tesseract-ocr/tessdata_best/main/{}.traineddata"
# Used in the release guide when not building on GitHub; GitHub builds fill in the real link.
SOURCE_URL = "https://github.com/swaidi/grepall"
IS_WINDOWS = os.name == "nt"
PLATFORM = "Windows" if IS_WINDOWS else "Linux"
APP_FOLDER = ROOT / "dist" / APP_NAME
EXECUTABLE = APP_FOLDER / (f"{APP_NAME}.exe" if IS_WINDOWS else APP_NAME)


def step(message: str) -> None:
    print(f"\n=== {message} ===", flush=True)


def app_version() -> str:
    text = (ROOT / APP_SCRIPT).read_text(encoding="utf-8")
    match = re.search(r'^APP_VERSION\s*=\s*"([^"]+)"', text, re.MULTILINE)
    return match.group(1) if match else "0.0.0"


def check_packages() -> None:
    step("Checking packages")
    missing = []
    packages = {"pymupdf": "pymupdf", "pymupdf4llm": "pymupdf4llm", "openpyxl": "openpyxl", "numpy": "numpy",
                "docx": "python-docx", "pptx": "python-pptx", "PyInstaller": "pyinstaller", "PIL": "pillow"}
    for module, package in packages.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    if missing:
        sys.exit(f"Missing packages: {', '.join(missing)}\n"
                 "Run the VS Code task '2. Install packages' first.")
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
        "--noconfirm", "--clean", "--onedir", "--windowed",
        "--name", APP_NAME,
        "--add-data", f"tessdata{separator}tessdata",
        "--collect-all", "pymupdf",
        "--collect-all", "pymupdf4llm",
        "--collect-all", "onnxruntime",
        "--collect-data", "docx",   # Word reading (templates and XML schemas)
        "--collect-data", "pptx",   # PowerPoint reading
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


def find_inno_setup() -> Path | None:
    """Locate ISCC.exe, the Inno Setup compiler."""
    found = shutil.which("ISCC") or shutil.which("iscc")
    if found:
        return Path(found)
    for base in (os.environ.get("ProgramFiles(x86)"), os.environ.get("ProgramFiles"),
                 str(Path(os.environ.get("LOCALAPPDATA", "")) / "Programs")):
        if base:
            candidate = Path(base) / "Inno Setup 6" / "ISCC.exe"
            if candidate.exists():
                return candidate
    return None


def build_installer(version: str, docs_dir: Path, release_dir: Path) -> Path | None:
    step("Building the Windows installer")
    compiler = find_inno_setup()
    if compiler is None and os.environ.get("GITHUB_ACTIONS"):
        print("Inno Setup not found; installing it with Chocolatey.")
        subprocess.run(["choco", "install", "innosetup", "-y", "--no-progress"], check=False)
        compiler = find_inno_setup()
    if compiler is None:
        if os.environ.get("GITHUB_ACTIONS"):
            sys.exit("Inno Setup could not be installed, so the installer was not built.")
        print("Inno Setup 6 is not installed, so the installer was skipped.\n"
              "The portable ZIP is still created. To build the installer too, install Inno Setup 6\n"
              "from https://jrsoftware.org/isinfo.php and run this task again.")
        return None

    icon = ROOT / "build" / "app_icon.ico"
    icon.parent.mkdir(exist_ok=True)
    from PIL import Image
    Image.open(ROOT / ICON).save(icon, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])

    command = [str(compiler), "/Q",
               f"/DAppVersion={version}", f"/DSourceDir={APP_FOLDER}", f"/DDocsDir={docs_dir}",
               f"/DIconFile={icon}", f"/DOutputDir={release_dir}", str(ROOT / "installer.iss")]
    if subprocess.run(command, cwd=ROOT).returncode != 0:
        sys.exit("\nInstaller build failed. Review the messages above.")
    setup = release_dir / f"{APP_NAME}-v{version}-Windows-Setup.exe"
    print(f"Installer: {setup}")
    return setup


def package() -> Path:
    version = app_version()
    step(f"Packaging release v{version} for {PLATFORM}")
    if not EXECUTABLE.exists():
        sys.exit(f"{EXECUTABLE} not found. Build the app first.")
    name = f"{APP_NAME}-v{version}-{PLATFORM}"
    release_dir = ROOT / "release"
    staging = release_dir / name
    shutil.rmtree(staging, ignore_errors=True)
    release_dir.mkdir(parents=True, exist_ok=True)

    shutil.copytree(APP_FOLDER, staging, symlinks=True)  # app plus its _internal folder
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

    if IS_WINDOWS and (ROOT / "installer.iss").exists():
        build_installer(version, staging, release_dir)

    archive_format = "zip" if IS_WINDOWS else "gztar"
    archive = shutil.make_archive(str(release_dir / name), archive_format, root_dir=release_dir, base_dir=name)
    shutil.rmtree(staging)
    print(f"Release archive: {archive}")
    return Path(archive)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build GrepAll.")
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
