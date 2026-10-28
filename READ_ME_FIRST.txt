GrepAll - Version {{VERSION}}
Offline OCR for PDFs and images, with Arabic support
Copyright (C) 2026 A.T.Grep
====================================================================

WHAT IT DOES
------------
Four independent tools for PDFs and document photos, plus a search library:
  - Make searchable (OCR): adds an invisible text layer to scanned pages.
  - Convert to Markdown: text for AI assistants, from PDFs, images, and
    Word, Excel and PowerPoint files.
  - Reduce file size: smaller PDFs with sharp text.
  - Tables to Excel: copies ruled tables, such as BOQs, into Excel.
  - Search documents: find any word across all your processed documents.

Arabic and English are supported. Everything runs on your computer;
no document is uploaded anywhere.


HOW TO START ON WINDOWS (RECOMMENDED: INSTALLER)
------------------------------------------------
1. Run GrepAll-v{{VERSION}}-Windows-Setup.exe. No administrator rights are needed.
2. Follow the steps. GrepAll is added to the Start menu, and a desktop
   shortcut is created if you keep that option selected.
3. To update later, run the setup of the newer version. Your settings are kept.
4. To remove GrepAll: Settings > Apps > Installed apps > GrepAll > Uninstall.

If Windows shows "Windows protected your PC", select "More info",
then "Run anyway".


PORTABLE VERSION ON WINDOWS (ZIP, NO INSTALLATION)
--------------------------------------------------
1. Extract the ZIP file to a permanent location, for example your Documents folder.
2. Open the extracted folder and double-click GrepAll.exe.

  ****************************************************************
  *  IMPORTANT: GrepAll.exe only works next to its "_internal"   *
  *  folder. Never copy GrepAll.exe alone to another place;      *
  *  it will show "Failed to load Python DLL".                   *
  *  To start it from the desktop, create a shortcut instead.    *
  ****************************************************************

To create a desktop shortcut:
  Right-click GrepAll.exe > Show more options > Send to > Desktop (create shortcut).
  (On Windows 10, "Send to" appears directly in the right-click menu.)


HOW TO START ON LINUX
---------------------
1. Extract the archive:
     tar -xzf GrepAll-v{{VERSION}}-Linux.tar.gz
2. Add the app to your applications menu (no sudo needed):
     cd GrepAll-v{{VERSION}}-Linux
     ./install_linux.sh
3. Open "GrepAll" from the applications menu,
   or run: grepall

After installing, you can delete the extracted folder.
To run the app without installing, use ./GrepAll inside the extracted folder.
To remove the app, run:
     bash ~/.local/share/grepall/install_linux.sh --uninstall

Requirements: 64-bit Linux with a desktop environment, such as
Ubuntu 22.04, Linux Mint 21, Debian 12, Fedora 38, or newer.


HOW TO USE
----------
The window has a sidebar on the left. Pick a tool; each one works on its own,
in any order. You do not need to run "Make searchable" first.

1. Add files with "Add files..." or "Add folder..." (PDF, JPG, PNG, TIFF, BMP,
   and for Convert to Markdown also DOCX, XLSX, XLSM and PPTX).
   The file list is shared by all tools, so you can switch tools freely.
   "Combine images into one document" merges all listed images, in list
   order, into one document (you choose its name when you start).
2. Choose where to save results ("Change..."), or keep "Same folder".
3. Set the tool's options, then select the blue button (for example
   "Make searchable"). Results appear in the Results table; double-click
   a row to open the file.

Common options:
  - Language: Arabic + English (default), English, or Arabic.
  - Scan quality: Standard (300 dpi) suits most documents.
    Use "Small print (400 dpi)" for small text such as BOQs or schedules.
  - Pages: leave blank for all pages, or enter a range such as 1-5, 9.

MAKE SEARCHABLE (OCR)
  Output: <name>_ocr.pdf, the same pages with searchable text.
  "Turn sideways and upside-down pages upright" (on by default) detects
  pages scanned the wrong way, makes them searchable, and shows them upright.

CONVERT TO MARKDOWN
  Output: <name>.md. Scanned pages are read automatically.
  "Also save the searchable PDF" saves <name>_ocr.pdf at the same time.
  Arabic cleanup (applied to the Markdown only): digits to 0-9, remove
  tatweel, remove diacritics, unify Alef forms.

  Word, Excel and PowerPoint files:
  - Word: headings, clause numbering (1.2, (a), iv), lists, bold/italic
    text and tables are kept.
  - Excel: one table per sheet. Formulas show their calculated values.
    If a file was not saved by Excel, results may be missing: open it in
    Excel, save it, and convert again. Hidden sheets are skipped.
  - PowerPoint: one section per slide, with tables and speaker notes.
  - Old formats (.doc, .xls, .ppt) are not supported: save them in the
    new format first. Pictures inside these files are not read.
  - Sensitive data hiding and Arabic cleanup work as for PDFs.

  Sensitive data (optional):
  - "Hide in Markdown" replaces ID/Iqama numbers, IBANs, phone numbers,
    email addresses and card numbers with labels such as [ID] or [IBAN].
  - "Hide these words" hides your own terms, such as company or person
    names (separate them with commas). They appear as [REDACTED].
  - "Hide the value after" hides what follows a label, while the label
    stays visible. Example: with "Ref, Dated", the line
      Ref: HMG-DAM-MEP-TEN-01  Dated: 08/10/2026
    becomes
      Ref: [REDACTED]  Dated: [REDACTED]
    The hidden value must contain a digit, such as a reference number
    or a date, so ordinary words after the label stay visible.
  - "Also create a redacted PDF copy" saves <name>_redacted.pdf with black
    boxes. The hidden text and image areas are permanently removed from
    that copy. The original files are never changed.
  Automatic detection can miss items, especially on poor scans.
  Always review redacted files before sharing them.

REDUCE FILE SIZE
  Output: <name>_small.pdf. Searchable text is kept.
  - Lossless: file structure only; quality unchanged, small savings.
  - Balanced (recommended): images at 200 dpi; text stays sharp.
  - Smallest: images at 150 dpi, stronger compression (e.g. for email).
  - "Convert colour pages to grayscale" saves more for black-and-white
    documents.
  If a file cannot be made smaller, nothing is saved and the Results
  table says so.

TABLES TO EXCEL
  Output: <name>_tables.xlsx, one sheet per table, with amounts stored as
  numbers so formulas work. Works for tables drawn with grid lines, in
  digital and scanned documents. Tables without lines are not detected.
  In scanned Arabic tables, check the numbers: Arabic-Indic digits and
  single small digits are often misread.

SEARCH DOCUMENTS (LIBRARY)
  Documents processed with "Make searchable" or "Convert to Markdown" are
  added automatically (this can be turned off). "Add documents..." adds
  existing files; scanned ones are read with OCR.
  Type words and select "Search". All words must appear on the same page;
  use quotes for an exact phrase, e.g. "chilled water". Arabic letter
  forms and digits are matched either way (الى finds إلى, 2026 finds ٢٠٢٦).
  Double-click a result to open the document; the page number is shown.
  "Remove missing files" cleans up documents that were moved or deleted.

SETTINGS
  Dark or light appearance (also the button at the top right), update
  check, and library options. Your options are remembered for the next
  start. "Reset all settings" restores the defaults.


TIPS
----
  - Pages that already contain text are copied without OCR, which saves time.
  - Phone photos and sideways scans are turned upright automatically.
  - Click "Activity" at the bottom to show the detailed log.
  - Select "Stop" to halt processing after the current page.
  - OCR accuracy depends on scan quality. Handwriting and stamps are
    recognized poorly.


UPDATES
-------
Once a day, GrepAll asks GitHub for the latest version number. If a newer
version exists, a bar with a "Download" button appears at the top of the
window. Only the version number is requested; no document, file name or
personal information is sent. Turn this off under Settings. Without an internet connection, the check is simply skipped.


FEEDBACK
--------
Select "Report a bug or suggest an improvement" at the bottom of the app.
The report opens as a new email in your email app; review it, then send.
You can also open an issue on the project page (link below).


LICENSE AND SOURCE CODE
-----------------------
This program is free software, licensed under the GNU Affero General Public
License version 3 (AGPL-3.0). See the LICENSE file included in this package.

It is provided WITHOUT ANY WARRANTY, without even the implied warranty of
merchantability or fitness for a particular purpose.

Source code and updates: {{SOURCE_URL}}

Third-party components and their licenses are listed in
THIRD_PARTY_NOTICES.md (open it with any text editor).
