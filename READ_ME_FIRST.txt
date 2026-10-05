GrepAll - Version {{VERSION}}
Offline OCR for PDFs and images, with Arabic support
Copyright (C) 2026 A.T.Grep
====================================================================

WHAT IT DOES
------------
Converts scanned PDF files and document photos into:
  - Searchable PDFs: the original pages with an invisible text layer added.
  - Markdown files (optional): structured text for AI assistants or documentation.

Arabic and English are supported. Everything runs on your computer;
no document is uploaded anywhere.


HOW TO START ON WINDOWS
-----------------------
1. Extract the ZIP file to a permanent location, for example your Documents folder.
2. Open the extracted folder and double-click GrepAll.exe. No installation is needed.

Important: GrepAll.exe needs the "_internal" folder next to it.
Keep the whole folder together; do not move GrepAll.exe out of it.

To create a desktop shortcut:
  Right-click GrepAll.exe > Show more options > Send to > Desktop (create shortcut).
  (On Windows 10, "Send to" appears directly in the right-click menu.)

If Windows shows "Windows protected your PC", select "More info",
then "Run anyway".


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
1. Select "Add files..." or "Add folder..." to choose PDFs or images
   (JPG, PNG, TIFF, BMP).
2. Optional settings:
   - Document language: Arabic + English (default), English, or Arabic.
   - Scan quality: Standard (300 dpi) suits most documents.
     Use "Small print (400 dpi)" for small text such as BOQs or schedules.
   - Pages: leave blank for all pages, or enter a range such as 1-5, 9.
   - Save to: by default, results are saved next to each original file.
   - Combine images into one PDF: merges all images in the list, in list
     order, into one PDF. Useful for documents photographed page by page.
     You choose the file name when OCR starts.
3. Select "Run OCR" and wait for "OCR finished" in the Activity box.
4. Select "Convert to Markdown" if you need Markdown files.
   Arabic cleanup options (applied to the Markdown only):
     - Convert Arabic-Indic digits to 0-9
     - Remove stretching (tatweel)
     - Remove diacritics (tashkeel)
     - Unify Alef forms
5. Select "Open output folder" to view the results.

Output files:
  <name>_ocr.pdf   Searchable PDF
  <name>.md        Markdown text

Your options are remembered for the next start.
Select "Reset settings" at the bottom of the window to restore the defaults.


TIPS
----
  - Pages that already contain text are copied without OCR, which saves time.
  - Phone photos are straightened to their correct orientation automatically.
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
