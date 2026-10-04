# Changelog

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
