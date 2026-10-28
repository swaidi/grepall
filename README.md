<p align="center">
  <img src="app_icon.png" alt="GrepAll icon" width="96">
</p>

<h1 align="center">GrepAll</h1>

<p align="center">
  <b>Offline OCR for PDFs and images, with Arabic support</b><br>
  A desktop app for Windows and Linux that turns scanned PDFs and document photos into searchable PDFs and clean Markdown files.
</p>

---

## Overview

GrepAll is an offline toolkit for scanned documents and document photos. It has four independent tools and a search library, so you can start with any of them:

| Tool | What it does | Output |
|---|---|---|
| **Make searchable (OCR)** | Adds an invisible text layer; pages stay unchanged | `<name>_ocr.pdf` |
| **Convert to Markdown** | Text for AI assistants such as Claude, from PDFs, images, Word, Excel and PowerPoint files; scanned pages are read automatically | `<name>.md` |
| **Reduce file size** | Recompresses images; text stays sharp and searchable | `<name>_small.pdf` |
| **Tables to Excel** | Copies ruled tables (such as BOQs) into Excel, with real numbers | `<name>_tables.xlsx` |
| **Search documents** | Finds words and reference numbers across all processed documents | Offline library |

All processing runs locally on your computer. No document is uploaded anywhere.

## Features

- Runs on **Windows** and **Linux**, with a Windows installer that needs no admin rights. Starts in about a second.
- Modern sidebar layout with a **dark theme** (default) and a light theme.
- Arabic and English text recognition, including mixed-language pages, with correct Arabic word order.
- **Sideways and upside-down scans** are detected, made searchable, and turned upright.
- **PDFs and images as input:** JPG, PNG, TIFF (including multi-page TIFF), and BMP. Images can be combined into one document.
- **Word, Excel and PowerPoint to Markdown** (`.docx`, `.xlsx`, `.xlsm`, `.pptx`): headings, automatic clause numbering (1.2, (a), iv), lists, bold and italic text, and tables from Word; one table per sheet from Excel, with calculated formula values and number formats; one section per slide from PowerPoint, including tables and speaker notes. These files can also be added to the library.
- **Reduce file size** with three levels (Lossless, Balanced, Smallest) and optional grayscale. A file is saved only if it really gets smaller.
- **Tables to Excel** for digital and scanned tables with grid lines; one sheet per table, amounts stored as numbers, right-to-left sheets for Arabic tables.
- **Searchable document library:** Arabic-aware search (letter forms, diacritics, and digit styles are matched either way), exact phrases in quotes, open results directly, and clean-up of moved or deleted files.
- **Arabic cleanup** for Markdown: Arabic-Indic digits to 0-9, tatweel and diacritics removal, unified Alef forms.
- **Sensitive data hiding:** Saudi ID/Iqama numbers, IBANs, phone numbers, emails, card numbers, your own words, and the values after labels you choose (such as "Ref" or "Dated"), with an optional redacted PDF copy in which they are permanently removed.
- Remembered settings, an optional update notice (only the version number is checked), and a built-in feedback form.
- Batch processing, page ranges, three scan-quality levels, and safe handling of large drawings (A0/A1).

## Download

Open the **[Releases](../../releases)** page and download the package for your system from the latest release:

| System | Package |
|---|---|
| Windows 10 or 11 (64-bit), **recommended** | `GrepAll-v<version>-Windows-Setup.exe` |
| Windows 10 or 11 (64-bit), portable | `GrepAll-v<version>-Windows.zip` |
| Linux (64-bit) | `GrepAll-v<version>-Linux.tar.gz` |

### Windows Installer (Recommended)

Run `GrepAll-v<version>-Windows-Setup.exe`. It installs GrepAll for the current user without administrator rights, adds it to the Start menu, and offers a desktop shortcut. Running a newer setup updates the app and keeps your settings. To remove it, use **Settings > Apps > Installed apps > GrepAll > Uninstall**.

### Windows Portable

1. Extract the ZIP file to a permanent location, such as your Documents folder.
2. Open the extracted folder and double-click `GrepAll.exe`.

> **Important:** `GrepAll.exe` only works next to its `_internal` folder. Copying the .exe alone elsewhere causes the error "Failed to load Python DLL." To start it from the desktop, create a shortcut instead: right-click `GrepAll.exe` > **Show more options** > **Send to** > **Desktop (create shortcut)**.

If Windows SmartScreen shows "Windows protected your PC," select **More info**, then **Run anyway**. The app is not digitally signed.

### Linux

```bash
tar -xzf GrepAll-v<version>-Linux.tar.gz
cd GrepAll-v<version>-Linux
./install_linux.sh
```

The installer adds **GrepAll** to your applications menu and the `grepall` command, for the current user only (no `sudo`). The extracted folder can be deleted afterward. To run the app without installing, use `./GrepAll` inside the extracted folder. To remove it, run `bash ~/.local/share/grepall/install_linux.sh --uninstall`.

The Linux build runs on Ubuntu 22.04, Linux Mint 21, Debian 12, Fedora 38, and newer distributions with a desktop environment.

## Usage

1. Pick a tool in the sidebar.
2. Select **Add files…** or **Add folder…**. The file list is shared by all tools, so you can switch tools freely.
3. Adjust the tool's options and select the blue button. Results appear in the **Results** table; double-click a row to open the file.

Outputs are saved next to each original file unless you choose another folder with **Change…**.

**Sensitive data (Convert to Markdown):** Select **Hide in Markdown**. Hidden items appear as `[ID]`, `[IBAN]`, `[PHONE]`, `[EMAIL]`, `[CARD]`, or `[REDACTED]`. Use **Hide these words** for names, and **Hide the value after** for labeled values: with `Ref, Dated`, the line `Ref: HMG-DAM-MEP-TEN-01 Dated: 08/10/2026` becomes `Ref: [REDACTED] Dated: [REDACTED]`. A hidden value must contain a digit. With **Also create a redacted PDF copy**, `<name>_redacted.pdf` is saved with black boxes; the hidden text and image areas are permanently removed from that copy. Automatic detection can miss items, so review redacted files before sharing them.

**Library:** Documents processed with **Make searchable** or **Convert to Markdown** are added automatically (optional). **Add documents…** adds existing files. All search words must appear on the same page; use quotes for an exact phrase.

Settings and the library are stored per user in `%APPDATA%\GrepAll\` (Windows) or `~/.config/grepall/` (Linux): `settings.json` and `library.db`.

## Build from Source

### Requirements

| | Windows | Linux (Debian, Ubuntu, Linux Mint) |
|---|---|---|
| Python | 3.10 or later from [python.org](https://www.python.org/downloads/) (per-user install, no admin rights needed) | `sudo apt install python3 python3-venv python3-tk` |
| Editor (recommended) | Visual Studio Code with the Python extension | Same |

On other distributions, install Python 3.10 or later with its `venv` and Tkinter packages.

### Build in VS Code (Windows and Linux)

1. Clone or download this repository and open its folder in VS Code (**File > Open Folder**).
2. Select **Terminal > Run Task…** and run the tasks in order:

   | Task | Purpose |
   |---|---|
   | `1. Create environment` | Creates the `.build-venv` Python environment |
   | `2. Install packages` | Installs the dependencies |
   | `3. Test app` | Downloads the OCR language data if needed, then runs the app from source |
   | `4. Build EXE` | Builds the app folder `dist/GrepAll/`, with `GrepAll.exe` (Windows) or `GrepAll` (Linux) inside |
   | `5. Package release` | Builds and creates a ready-to-share archive in `release/` |

Each system builds only its own version. To build both, use the GitHub workflow below, or run the tasks on each system.

### Build from the Command Line

**Windows (PowerShell):**

```powershell
python -m venv .build-venv
.build-venv\Scripts\python.exe -m pip install -r requirements.txt pyinstaller pillow
.build-venv\Scripts\python.exe build_exe.py --package
```

**Linux:**

```bash
python3 -m venv .build-venv
.build-venv/bin/python -m pip install -r requirements.txt pyinstaller pillow
.build-venv/bin/python build_exe.py --package
```

On Windows, `--package` also builds the installer if [Inno Setup 6](https://jrsoftware.org/isinfo.php) is installed (free; a per-user installation works). Without it, the installer step is skipped and the portable ZIP is still created.

`build_exe.py` downloads the OCR language data (`eng`, `ara`) during the first build. If the download is blocked, download `eng.traineddata` and `ara.traineddata` from [tessdata_best](https://github.com/tesseract-ocr/tessdata_best) in a browser and save them in a `tessdata` folder in the project.

### Automatic Builds on GitHub

`.github/workflows/release.yml` builds both versions on GitHub:

- **Publishing a release** builds the Windows installer, the Windows portable ZIP, and the Linux package, and attaches them to that release automatically.
- **Running the workflow manually** (Actions tab > **Build release** > **Run workflow**) creates test builds, available under the run's **Artifacts**.

### Project Structure

```
├── .github/workflows/release.yml   Windows and Linux builds on GitHub
├── .vscode/                        VS Code tasks and settings (Windows and Linux)
├── app_icon.png                    App icon
├── build_exe.py                    Build and packaging script
├── install_linux.sh                Linux menu installer (included in the Linux package)
├── installer.iss                   Windows installer definition (Inno Setup)
├── pdf_ocr_standalone.py           Application source code
├── READ_ME_FIRST.txt               User guide (included in the release packages)
├── requirements.txt                Python dependencies
├── CHANGELOG.md
├── LICENSE
└── THIRD_PARTY_NOTICES.md
```

## Known Limitations

- Tables to Excel needs tables drawn with grid lines. In scanned Arabic tables, Arabic-Indic digits and single small digits are often misread; check the numbers.
- The library opens a document but cannot jump to the page; the page number is shown instead.
- Older Office formats (`.doc`, `.xls`, `.ppt`) are not supported; save them as `.docx`, `.xlsx` or `.pptx` first. Images, text boxes, headers and footers inside Word files are not converted. Excel formulas show the result last saved by Excel; files created by other programs may have no saved results. Hidden Excel sheets are skipped, and each sheet is limited to 20,000 rows.
- WEBP and HEIC images are not supported. Convert them to JPG or PNG first.
- OCR accuracy depends on scan quality. Handwriting, stamps, and signatures are recognized poorly.
- Arabic file names and search excerpts may display with reversed letter order in the app window on Linux. Processing and search are not affected.
- Languages other than Arabic and English require additional language data and a code change.

## Contributing

Contributions are welcome:

- **Bug reports and suggestions:** Use the **Report a bug or suggest an improvement** button in the app, or open an [issue](../../issues).
- **Code changes:** Fork the repository, make your changes, and open a pull request with a short description of what changed and why. If possible, test on both Windows and Linux.

Under the AGPL-3.0 license, modified versions that you share must also be published under AGPL-3.0, with the original copyright notice kept.

## License

Copyright © 2026 A.T.Grep

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, version 3. See [LICENSE](LICENSE) for the full text.

This program is distributed in the hope that it will be useful, but **without any warranty**, without even the implied warranty of merchantability or fitness for a particular purpose.

The app includes third-party components under their own licenses. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
