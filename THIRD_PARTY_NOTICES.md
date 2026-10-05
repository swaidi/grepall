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

## Build Tools (Not Distributed as Libraries)

| Tool | License |
|---|---|
| [PyInstaller](https://pyinstaller.org/) | GPL v2 or later, with an exception that permits distributing the built application under any license |
| [Pillow](https://python-pillow.org/) | MIT-CMU License (used only to convert the icon at build time) |

The full license texts are available from each project's website or repository.
