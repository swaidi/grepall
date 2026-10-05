# Changelog

## 1.4.0 (2026-10-05)

### Changed name
- The app is now named **GrepAll**, with the tagline "Offline OCR for PDFs and images, with Arabic support." It was previously released as "PDF OCR to Markdown." Saved settings are carried over automatically, and the Linux installer replaces the previous installation.

### Added
- Images as input: JPG, PNG, TIFF (including multi-page TIFF), and BMP. Phone photos are turned upright automatically and placed on A4-sized pages.
- "Combine images into one PDF" option, for documents photographed page by page.
- Arabic cleanup options for the Markdown output: convert Arabic-Indic digits, remove tatweel, remove diacritics, and unify Alef forms.
- Remembered settings: language, scan quality, output folder, Markdown and Arabic cleanup options, and window size are restored at each start. A "Reset settings" button restores the defaults.

### Changed
- The app is distributed as a folder instead of a single file, so it starts in about a second instead of several seconds. Keep `GrepAll.exe` (or `GrepAll` on Linux) together with its `_internal` folder.
- The Linux installer keeps a copy of itself for uninstalling, so the extracted folder can be deleted after installation.

## 1.3.0 (2026-10-04)

### Added
- Linux support: a ready-to-run Linux build and `install_linux.sh`, which adds the app to the applications menu with its icon.
- Automatic Windows and Linux builds on GitHub for each published release.
- `5. Package release` VS Code task, which creates a ready-to-share archive for the current system.

### Changed
- VS Code tasks work on both Windows and Linux.
- The feedback email and "Open output folder" use each system's default application.
- The header title uses the system's default font instead of a Windows-only font.

## 1.2.0 (2026-10-04)

### Added
- App icon in the window header, title bar, pop-up windows, and the Windows `.exe` file.

## 1.1.0 (2026-10-01)

### Added
- Form to report a bug or suggest an improvement, sent through the user's email app.
- "A.T.Grep" credit under the Activity box.

### Changed
- Searchable PDFs keep the original pages unchanged and add only an invisible text layer, so output files stay close to the original size.
- Standard (300 dpi) is the default scan quality.

### Fixed
- Stopping a run no longer deletes previous outputs.
- Buttons reliably re-enable after each run.
- Large drawings are processed at a safe resolution to prevent memory errors.
- Files are saved through a temporary file, so an interrupted save cannot corrupt them.
- Number sequences in Arabic lines keep their order in the Markdown output.

## 1.0.0

- First release: OCR of scanned PDFs into searchable PDFs, with optional Markdown conversion.
