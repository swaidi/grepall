# Changelog

## 1.6.0 (2026-10-28)

### Added
- **Independent tools:** Make searchable, Convert to Markdown, Reduce file size, and Tables to Excel each work on their own, in any order. Markdown no longer requires running OCR first; scanned pages are read automatically.
- **Reduce file size:** Lossless, Balanced, and Smallest levels, optional grayscale, before/after sizes; nothing is saved if a file cannot be made smaller.
- **Tables to Excel:** Ruled tables from digital and scanned documents, one sheet per table, amounts stored as numbers, right-to-left sheets for Arabic tables.
- **Searchable document library:** Offline, Arabic-aware search across processed documents, with automatic adding, "Add documents…", open document or folder, and clean-up of missing files.
- **Sideways page fix:** Pages scanned sideways or upside down are detected, made searchable, and shown upright.
- **Word, Excel and PowerPoint to Markdown:** `.docx` (headings, automatic clause numbering, lists, bold/italic, tables), `.xlsx`/`.xlsm` (one table per sheet, calculated values, number formats, warning when formula results are missing), and `.pptx` (one section per slide, tables, speaker notes). Sensitive data hiding, Arabic cleanup and the library work with these files too.
- Visible progress next to the run button: a moving bar from the first click, percentage, file count, elapsed time, and "Finished in m:ss" at the end.
- "Hide the value after" for sensitive data, e.g. the reference number after "Ref" and the date after "Dated".

### Changed
- New design matching GrepMail and SysHealth: top bar, sidebar navigation, shared file list, Results table, collapsible Activity log, and status bar.
- Dark theme is the default; a light theme is one click away.
- Feedback, update check, and project link moved to "About & feedback"; options remembered as before.

## 1.5.0 (2026-10-10)

### Added
- **Windows installer:** `GrepAll-v1.5.0-Windows-Setup.exe` installs GrepAll for the current user without administrator rights, adds it to the Start menu, offers a desktop shortcut, keeps settings when updating, and can be removed from Settings > Apps. The portable ZIP remains available.
- **Sensitive data hiding:** Optional hiding of Saudi ID/Iqama numbers, IBANs, phone numbers, email addresses, card numbers, custom words, and the values after chosen labels (for example the reference number after "Ref" and the date after "Dated") in the Markdown output, with an optional redacted PDF copy in which the hidden text and image areas are permanently removed.
- **Update notice:** A once-a-day check for a newer release on GitHub, shown as a bar with a Download button. Only the version number is requested. It can be turned off under Options.

### Changed
- Searchable PDFs no longer keep a hidden full-page copy of the scan inside the text layer, which also makes redaction reliable.
- The portable Windows guide warns more clearly that `GrepAll.exe` must stay next to its `_internal` folder.

### Fixed
- The file list buttons stay fully visible when the window is short.

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
