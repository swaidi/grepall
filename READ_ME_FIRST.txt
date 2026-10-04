PDF OCR to Markdown - Version {{VERSION}}
Copyright (C) 2026 A.T.Grep
====================================================================

WHAT IT DOES
------------
Converts scanned PDF files into:
  - Searchable PDFs: the original pages with an invisible text layer added.
  - Markdown files (optional): structured text for AI assistants or documentation.

Arabic and English are supported. Everything runs on your computer;
no document is uploaded anywhere.


HOW TO START ON WINDOWS
-----------------------
1. Extract the ZIP file to any folder, for example your Documents folder.
2. Double-click PDF-OCR.exe. No installation is needed.

Notes:
  - The window may take several seconds to appear at each start.
  - If Windows shows "Windows protected your PC", select "More info",
    then "Run anyway".


HOW TO START ON LINUX
---------------------
1. Extract the archive:
     tar -xzf PDF-OCR-v{{VERSION}}-Linux.tar.gz
2. Add the app to your applications menu (no sudo needed):
     cd PDF-OCR-v{{VERSION}}-Linux
     ./install_linux.sh
3. Open "PDF OCR to Markdown" from the applications menu,
   or run: pdf-ocr

To run it without installing, use: ./PDF-OCR
To remove it, run: ./install_linux.sh --uninstall

Requirements: 64-bit Linux with a desktop environment, such as
Ubuntu 22.04, Linux Mint 21, Debian 12, Fedora 38, or newer.


HOW TO USE
----------
1. Select "Add files..." or "Add folder..." to choose your PDFs.
2. Optional settings:
   - Document language: Arabic + English (default), English, or Arabic.
   - Scan quality: Standard (300 dpi) suits most documents.
     Use "Small print (400 dpi)" for small text such as BOQs or schedules.
   - Pages: leave blank for all pages, or enter a range such as 1-5, 9.
   - Save to: by default, results are saved next to each original PDF.
3. Select "Run OCR" and wait for "OCR finished" in the Activity box.
4. Select "Convert to Markdown" if you need Markdown files.
5. Select "Open output folder" to view the results.

Output files:
  <name>_ocr.pdf   Searchable PDF
  <name>.md        Markdown text


TIPS
----
  - Pages that already contain text are copied without OCR, which saves time.
  - Select "Stop" to halt processing after the current page.
  - OCR accuracy depends on scan quality. Handwriting and stamps are
    recognized poorly.


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
