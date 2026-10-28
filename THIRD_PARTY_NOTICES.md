# Third-Party Notices

GrepAll is licensed under the GNU Affero General Public License v3.0 (see `LICENSE`).
The distributed GrepAll app (`GrepAll.exe` on Windows, `GrepAll` on Linux) bundles the following third-party components, each under its own license.

## Main Components

| Component | Purpose | License |
|---|---|---|
| [PyMuPDF](https://github.com/pymupdf/PyMuPDF) (includes MuPDF and the Tesseract OCR engine) | PDF reading, rendering and OCR | GNU AGPL v3.0 (Artifex Software, Inc.) |
| [pymupdf4llm](https://github.com/pymupdf/pymupdf4llm) | PDF to Markdown conversion | GNU AGPL v3.0 (Artifex Software, Inc.) |
| pymupdf-layout | Page layout analysis | GNU AGPL v3.0 (Artifex Software, Inc.) |
| [Tesseract tessdata_best](https://github.com/tesseract-ocr/tessdata_best) (`eng`, `ara`) | OCR language data | Apache License 2.0 |
| [ONNX Runtime](https://github.com/microsoft/onnxruntime) | Layout model inference | MIT License |
| [Python](https://www.python.org/) | Runtime | Python Software Foundation License |
| Tcl/Tk (Tkinter) | User interface | Tcl/Tk License (BSD-style) |

## Supporting Python Packages

| Package | License |
|---|---|
| NumPy | BSD 3-Clause |
| NetworkX | BSD 3-Clause |
| SymPy, mpmath | BSD |
| protobuf | BSD 3-Clause |
| FlatBuffers | Apache License 2.0 |
| packaging | Apache License 2.0 or BSD 2-Clause |
| psutil | BSD 3-Clause |
| tabulate | MIT License |
| PyYAML | MIT License |
| [openpyxl](https://openpyxl.readthedocs.io/) | MIT License (writes the Excel files) |
| et_xmlfile | MIT License |
| [python-docx](https://github.com/python-openxml/python-docx) | MIT License (reads Word files) |
| [python-pptx](https://github.com/scanny/python-pptx) | MIT License (reads PowerPoint files) |
| [lxml](https://lxml.de/) (includes libxml2 and libxslt) | BSD 3-Clause (libxml2 and libxslt: MIT License) |
| Pillow | MIT-CMU License |
| XlsxWriter | BSD 2-Clause |
| typing_extensions | Python Software Foundation License |

## Build Tools (Not Distributed as Libraries)

| Tool | License |
|---|---|
| [PyInstaller](https://pyinstaller.org/) | GPL v2 or later, with an exception that permits distributing the built application under any license |
| [Pillow](https://python-pillow.org/) | MIT-CMU License (converts the icon at build time; also used at run time by python-pptx) |
| [Inno Setup](https://jrsoftware.org/isinfo.php) | Inno Setup License (permissive); builds the Windows installer, whose setup program is part of `GrepAll-…-Windows-Setup.exe` |

The full license texts are available from each project's website or repository.
