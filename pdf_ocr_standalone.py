#!/usr/bin/env python3
# GrepAll - Offline OCR for PDFs and images, with Arabic support
# Copyright (C) 2026 A.T.Grep
# Licensed under the GNU Affero General Public License v3.0. See LICENSE.
"""GrepAll - single-file desktop app for Windows and Linux.

Creates searchable PDFs (original pages kept unchanged, invisible OCR text layer added)
and optionally converts them to Markdown.

Dependencies: python -m pip install pymupdf pymupdf4llm
Tesseract language data (eng.traineddata, ara.traineddata) is also required, either
installed with Tesseract or placed in a "tessdata" folder next to this script or the .exe.
"""
from __future__ import annotations

import json
import math
import os
import platform
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import tkinter as tk
import tkinter.font as tkfont
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from urllib.parse import quote

try:
    import pymupdf
except ImportError:
    try:
        import fitz as pymupdf
    except ImportError as exc:
        raise SystemExit("PyMuPDF is required: python -m pip install pymupdf") from exc

APP_NAME = "GrepAll"
APP_TAGLINE = "Offline OCR for PDFs and images, with Arabic support"
APP_VERSION = "1.4.0"
APP_CREDIT = "A.T.Grep"
FEEDBACK_EMAIL = "dev.oasis006@passmail.net"
ICON_FILE = "app_icon.png"


def resource_path(name: str) -> Path:
    """Locate a bundled file, both when running as a script and as a PyInstaller .exe."""
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)) / name

MIN_TEXT_CHARS = 25
MAX_RENDER_PIXELS = 60_000_000  # caps memory use on large drawings (A0/A1)
MAILTO_SAFE_LENGTH = 1800       # longer mailto links are truncated by some mail apps
LANGUAGES = {"Arabic + English": "ara+eng", "English": "eng", "Arabic": "ara"}
RESOLUTIONS = {"Compact (200 dpi)": 200, "Standard (300 dpi)": 300, "Small print (400 dpi)": 400}
ARABIC = re.compile(r"[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]")
LTR_CHARS = re.compile(r"[A-Za-z0-9\u0660-\u0669]")
MD_PREFIX = re.compile(r"^(\s*(?:#{1,6}\s+|[-*+]\s+|>\s+)?)(.*)$")
IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp")
INPUT_SUFFIXES = (".pdf",) + IMAGE_SUFFIXES
IMAGE_PAGE_LONG_SIDE = 842  # images are placed on A4-sized pages (842 pt = 297 mm)
ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹٫٬٪", "01234567890123456789.,%")
ARABIC_DIACRITICS = re.compile(r"[\u064B-\u065F\u0670]")
ALEF_FORMS = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا"})
TATWEEL = "\u0640"

DEFAULT_SETTINGS = {
    "language": "Arabic + English",
    "quality": "Standard (300 dpi)",
    "output_dir": "",
    "combine_images": False,
    "markers": True,
    "strip_headers": False,
    "arabic_digits": True,
    "arabic_tatweel": True,
    "arabic_diacritics": True,
    "arabic_alef": True,
    "window_size": "880x860",
}


def settings_path() -> Path:
    """Per-user settings file: %APPDATA%\\GrepAll on Windows, ~/.config/grepall on Linux."""
    return _settings_base() / ("GrepAll" if sys.platform.startswith("win") else "grepall") / "settings.json"


def _settings_base() -> Path:
    if sys.platform.startswith("win"):
        return Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
    return Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")


def _migrate_old_settings() -> None:
    """Copy settings saved by versions released as "PDF OCR to Markdown", once."""
    new = settings_path()
    old = _settings_base() / ("PDF-OCR" if sys.platform.startswith("win") else "pdf-ocr") / "settings.json"
    if new.exists() or not old.exists():
        return
    try:
        new.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(old, new)
    except OSError:
        pass


def load_settings() -> dict:
    _migrate_old_settings()
    settings = dict(DEFAULT_SETTINGS)
    try:
        stored = json.loads(settings_path().read_text(encoding="utf-8"))
    except Exception:
        return settings
    for key, default in DEFAULT_SETTINGS.items():
        value = stored.get(key)
        if isinstance(value, type(default)):
            settings[key] = value
    if settings["language"] not in LANGUAGES:
        settings["language"] = DEFAULT_SETTINGS["language"]
    if settings["quality"] not in RESOLUTIONS:
        settings["quality"] = DEFAULT_SETTINGS["quality"]
    if not re.fullmatch(r"\d{3,4}x\d{3,4}", settings["window_size"]):
        settings["window_size"] = DEFAULT_SETTINGS["window_size"]
    return settings


def save_settings(settings: dict) -> None:
    path = settings_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_name(path.name + ".partial")
        temp.write_text(json.dumps(settings, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(temp, path)
    except OSError:
        pass  # settings are a convenience; never block the app


def is_image(path: Path) -> bool:
    return path.suffix.lower() in IMAGE_SUFFIXES


def images_to_pdf(images: list[Path], dst: Path) -> int:
    """Combine image files into one PDF with A4-sized pages. Multi-page TIFFs add one page per frame.
    JPEG data is kept as is, and phone-photo rotation (EXIF) is respected. Returns the page count."""
    output = pymupdf.open()
    try:
        for image in images:
            with pymupdf.open(image) as image_doc:
                pdf_bytes = image_doc.convert_to_pdf()
            with pymupdf.open("pdf", pdf_bytes) as image_pdf:
                for index, page in enumerate(image_pdf):
                    scale = IMAGE_PAGE_LONG_SIDE / max(page.rect.width, page.rect.height)
                    new_page = output.new_page(width=page.rect.width * scale, height=page.rect.height * scale)
                    new_page.show_pdf_page(new_page.rect, image_pdf, index)
        if output.page_count == 0:
            raise RuntimeError("The image contains no pages.")
        output.save(dst, garbage=4, deflate=True)
        return output.page_count
    finally:
        output.close()


def clean_arabic(text: str, digits: bool, tatweel: bool, diacritics: bool, alef: bool) -> str:
    """Optional Arabic normalization for the Markdown output."""
    if digits:
        text = text.translate(ARABIC_DIGITS)
    if tatweel:
        text = text.replace(TATWEEL, "")
    if diacritics:
        text = ARABIC_DIACRITICS.sub("", text)
    if alef:
        text = text.translate(ALEF_FORMS)
    return text


# =============================================================== engine
def find_tessdata(explicit: str | None = None) -> str:
    candidates: list[str] = []
    if explicit:
        candidates.append(explicit)
    if getattr(sys, "frozen", False):
        candidates.extend((str(Path(getattr(sys, "_MEIPASS", "")) / "tessdata"),
                           str(Path(sys.executable).parent / "tessdata")))
    candidates.append(str(Path(__file__).resolve().parent / "tessdata"))
    if os.environ.get("TESSDATA_PREFIX"):
        candidates.append(os.environ["TESSDATA_PREFIX"])
    try:
        found = pymupdf.get_tessdata()
        if found:
            candidates.append(found)
    except Exception:
        pass
    candidates.extend((
        "/usr/share/tesseract-ocr/5/tessdata",
        "/usr/share/tesseract-ocr/4.00/tessdata",
        "/usr/share/tessdata",
        "/usr/local/share/tessdata",
        "/opt/homebrew/share/tessdata",
        r"C:\Program Files\Tesseract-OCR\tessdata",
        str(Path.home() / "AppData/Local/Programs/Tesseract-OCR/tessdata"),
    ))
    for folder in candidates:
        path = Path(folder) if folder else None
        if path and path.is_dir() and any(path.glob("*.traineddata")):
            return str(path)
    raise FileNotFoundError("Tesseract language data was not found. "
                            "Install Tesseract, or put a tessdata folder next to this app.")


def check_languages(tessdata: str, lang: str) -> None:
    missing = [item for item in lang.split("+") if not (Path(tessdata) / f"{item}.traineddata").is_file()]
    if missing:
        raise FileNotFoundError(f"Missing language data: {', '.join(missing)}\nExpected in: {tessdata}")


def parse_pages(spec: str | None, count: int) -> list[int]:
    """Convert a 1-based page selection such as '1-5, 9' to zero-based indexes."""
    if not spec:
        return list(range(count))
    result: set[int] = set()
    for part in spec.replace(" ", "").split(","):
        if not part:
            continue
        if "-" in part:
            first, last = part.split("-", 1)
            start, end = int(first), int(last) if last else count
        else:
            start = end = int(part)
        if start > end:
            start, end = end, start
        result.update(page - 1 for page in range(start, end + 1) if 1 <= page <= count)
    if not result:
        raise ValueError(f"No valid pages in '{spec}'. This PDF has {count} pages.")
    return sorted(result)


class Cancelled(Exception):
    pass


def safe_dpi(page, dpi: int) -> int:
    """Lower the render resolution for very large pages so memory use stays bounded."""
    pixels = page.rect.width * page.rect.height * (dpi / 72) ** 2
    if pixels <= MAX_RENDER_PIXELS:
        return dpi
    return max(72, int(72 * math.sqrt(MAX_RENDER_PIXELS / (page.rect.width * page.rect.height))))


def ocr_pdf(src: Path, dst: Path, pages: list[int], lang: str, dpi: int,
            tessdata: str, force: bool, progress=None) -> tuple[int, int]:
    """Keep each original page unchanged and add only an invisible OCR text layer.
    Returns (OCR page count, copied page count)."""
    doc = pymupdf.open(src)
    if doc.needs_pass:
        doc.close()
        raise RuntimeError("The PDF is password-protected.")
    output = pymupdf.open()
    temp = dst.with_name(dst.stem + ".partial.pdf")
    ocr_count = copied_count = 0
    try:
        for position, page_number in enumerate(pages, 1):
            page = doc[page_number]
            output.insert_pdf(doc, from_page=page_number, to_page=page_number)
            has_text = len(page.get_text("text").strip()) >= MIN_TEXT_CHARS
            if has_text and not force:
                copied_count += 1
                status = "text layer found, copied"
            else:
                target = output[-1]
                rotation = target.rotation
                target.set_rotation(0)  # OCR in unrotated page coordinates
                page_dpi = safe_dpi(target, dpi)
                pixmap = target.get_pixmap(dpi=page_dpi)
                pixmap.set_dpi(page_dpi, page_dpi)
                ocr_bytes = pixmap.pdfocr_tobytes(compress=True, language=lang, tessdata=tessdata)
                pixmap = None  # release memory
                with pymupdf.open("pdf", ocr_bytes) as ocr_doc:
                    ocr_page = ocr_doc[0]
                    for image in ocr_page.get_images(full=True):
                        ocr_page.delete_image(image[0])  # discard the large raster, keep the text
                    target.show_pdf_page(target.rect, ocr_doc, 0, overlay=True)
                target.set_rotation(rotation)
                ocr_count += 1
                status = "OCR done" if page_dpi == dpi else f"OCR done (large page, read at {page_dpi} dpi)"
            if progress:
                progress(position, len(pages), page_number + 1, status)
        output.save(temp, garbage=4, deflate=True, use_objstms=True)
        output.close()
        os.replace(temp, dst)  # the final file only appears once it is complete
    finally:
        if not output.is_closed:
            output.close()
        doc.close()
        if temp.exists():
            try:
                temp.unlink()
            except OSError:
                pass
    return ocr_count, copied_count


def is_ocr_page(page) -> bool:
    """True when the page's text layer was produced by Tesseract (invisible GlyphLessFont)."""
    return any("GlyphLess" in font[3] for font in page.get_fonts(full=True))


def fix_rtl_line(line: str) -> str:
    """Tesseract stores Arabic words in visual order; restore logical order for
    Arabic-dominant lines while keeping English words and number sequences intact."""
    prefix, body = MD_PREFIX.match(line).groups()
    if len(ARABIC.findall(body)) <= len(re.findall(r"[A-Za-z]", body)):
        return line
    groups: list[list[str]] = []
    for token in body.split():
        ltr_token = bool(LTR_CHARS.search(token) and not ARABIC.search(token))
        if ltr_token and groups and groups[-1][0] == "L":
            groups[-1].append(token)
        else:
            groups.append(["L" if ltr_token else "R", token])
    return prefix + " ".join(" ".join(group[1:]) for group in reversed(groups))


def to_markdown(pdf_path: Path, md_path: Path, title: str, page_numbers: list[int],
                markers: bool, strip_headers: bool = False, cleanup: dict | None = None) -> str | None:
    """Write Markdown. Returns a warning message when the layout engine was not used."""
    texts: list[str] = []
    warning = None
    try:
        import pymupdf4llm
        common = dict(page_chunks=True, write_images=False, show_progress=False)
        try:
            data = pymupdf4llm.to_markdown(str(pdf_path), use_ocr=False, header=not strip_headers,
                                           footer=not strip_headers, **common)
        except TypeError:
            data = pymupdf4llm.to_markdown(str(pdf_path), ignore_images=True, **common)
        texts = [chunk.get("text", "") for chunk in data]
    except ImportError:
        warning = "pymupdf4llm is not installed; plain text layout was used."
    except Exception as exc:
        warning = f"Layout conversion failed ({exc}); plain text layout was used."

    chunks: list[str] = []
    with pymupdf.open(pdf_path) as doc:
        for index, page in enumerate(doc):
            body = texts[index].strip() if index < len(texts) else ""
            if not body:
                body = page.get_text("text", sort=True).strip() or "_[no text on this page]_"
            if is_ocr_page(page):
                body = "\n".join(fix_rtl_line(line) for line in body.splitlines())
            if cleanup:
                body = clean_arabic(body, **cleanup)
            number = page_numbers[index] if index < len(page_numbers) else index + 1
            header = f"<!-- Page {number} -->\n\n" if markers else ""
            chunks.append(header + body)
    temp = md_path.with_name(md_path.name + ".partial")
    temp.write_text(f"# {title}\n\n" + "\n\n".join(chunks) + "\n", encoding="utf-8")
    os.replace(temp, md_path)
    return warning


# =============================================================== feedback form
class FeedbackDialog(tk.Toplevel):
    """Collects a bug report or improvement suggestion and opens it in the user's email app."""

    TYPES = ("Bug report", "Improvement suggestion")

    def __init__(self, parent: "PdfOcrApp") -> None:
        super().__init__(parent)
        self.parent = parent
        self.title("Report a bug or suggest an improvement")
        self.transient(parent)
        self.resizable(True, True)
        self.minsize(520, 520)

        self.kind = tk.StringVar(value=self.TYPES[0])
        self.summary = tk.StringVar()
        self.name = tk.StringVar()
        self.include_system = tk.BooleanVar(value=True)
        self.include_log = tk.BooleanVar(value=True)

        body = ttk.Frame(self, padding=16)
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(3, weight=1)
        body.rowconfigure(4, weight=1)

        ttk.Label(body, text="Type").grid(row=0, column=0, sticky="w", pady=4)
        types = ttk.Frame(body)
        types.grid(row=0, column=1, sticky="w", pady=4)
        for value in self.TYPES:
            ttk.Radiobutton(types, text=value, value=value, variable=self.kind,
                            command=self._toggle_steps).pack(side="left", padx=(0, 16))

        ttk.Label(body, text="Summary *").grid(row=1, column=0, sticky="w", pady=4)
        self.summary_entry = ttk.Entry(body, textvariable=self.summary)
        self.summary_entry.grid(row=1, column=1, sticky="ew", pady=4)

        ttk.Label(body, text="Your name").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Entry(body, textvariable=self.name).grid(row=2, column=1, sticky="ew", pady=4)

        ttk.Label(body, text="Details *").grid(row=3, column=0, sticky="nw", pady=4)
        self.details = tk.Text(body, height=6, wrap="word")
        self.details.grid(row=3, column=1, sticky="nsew", pady=4)

        self.steps_label = ttk.Label(body, text="Steps to\nreproduce")
        self.steps_label.grid(row=4, column=0, sticky="nw", pady=4)
        self.steps = tk.Text(body, height=4, wrap="word")
        self.steps.grid(row=4, column=1, sticky="nsew", pady=4)
        self.steps.insert("1.0", "1. \n2. \n3. ")

        ttk.Checkbutton(body, text="Include app and system information", variable=self.include_system)\
            .grid(row=5, column=1, sticky="w", pady=(8, 0))
        ttk.Checkbutton(body, text="Include recent activity log", variable=self.include_log)\
            .grid(row=6, column=1, sticky="w")

        ttk.Label(body, text=f"The report opens as a new email to {FEEDBACK_EMAIL} in your email app. "
                             "Review it there, then select Send.",
                  foreground="#555", wraplength=460, justify="left")\
            .grid(row=7, column=0, columnspan=2, sticky="w", pady=(12, 0))

        buttons = ttk.Frame(body)
        buttons.grid(row=8, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(side="right")
        ttk.Button(buttons, text="Copy report", command=self.copy_report).pack(side="right", padx=8)
        ttk.Button(buttons, text="Open in email app", command=self.send).pack(side="right")

        self.bind("<Escape>", lambda _event: self.destroy())
        self.summary_entry.focus_set()
        self.grab_set()
        self._center_on_parent()

    def _center_on_parent(self) -> None:
        self.update_idletasks()
        x = self.parent.winfo_rootx() + (self.parent.winfo_width() - self.winfo_width()) // 2
        y = self.parent.winfo_rooty() + (self.parent.winfo_height() - self.winfo_height()) // 3
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    def _toggle_steps(self) -> None:
        state = "normal" if self.kind.get() == self.TYPES[0] else "disabled"
        self.steps.configure(state=state)

    def _validate(self) -> bool:
        if not self.summary.get().strip():
            messagebox.showwarning("Summary required", "Enter a short summary.", parent=self)
            self.summary_entry.focus_set()
            return False
        if not self.details.get("1.0", "end").strip():
            messagebox.showwarning("Details required", "Describe the issue or suggestion.", parent=self)
            self.details.focus_set()
            return False
        return True

    def _subject(self) -> str:
        tag = "Bug" if self.kind.get() == self.TYPES[0] else "Suggestion"
        return f"[{APP_NAME} {APP_VERSION}] {tag}: {self.summary.get().strip()}"

    def _report(self, log_lines: int = 15) -> str:
        parts = [f"Type: {self.kind.get()}", f"Summary: {self.summary.get().strip()}"]
        if self.name.get().strip():
            parts.append(f"Submitted by: {self.name.get().strip()}")
        parts += ["", "Details:", self.details.get("1.0", "end").strip()]
        steps = self.steps.get("1.0", "end").strip()
        if self.kind.get() == self.TYPES[0] and re.search(r"\d\.\s*\S", steps):
            parts += ["", "Steps to reproduce:", steps]
        if self.include_system.get():
            parts += ["", "System:", system_info()]
        if self.include_log.get() and log_lines:
            log = self.parent.recent_log(log_lines)
            if log:
                parts += ["", "Recent activity:", log]
        return "\n".join(parts)

    def _copy_to_clipboard(self, text: str) -> None:
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()

    def copy_report(self) -> None:
        if not self._validate():
            return
        self._copy_to_clipboard(f"To: {FEEDBACK_EMAIL}\nSubject: {self._subject()}\n\n{self._report()}")
        messagebox.showinfo("Report copied",
                            f"The report is copied to the clipboard.\nPaste it into an email to {FEEDBACK_EMAIL}.",
                            parent=self)

    def send(self) -> None:
        if not self._validate():
            return
        full_report = self._report()
        subject = quote(self._subject())

        # Fit the link within mail-app limits: drop the log first, then shorten the text.
        body_text = full_report
        for log_lines in (15, 5, 0):
            body_text = self._report(log_lines)
            if len(subject) + len(quote(body_text)) < MAILTO_SAFE_LENGTH:
                break
        truncated = len(subject) + len(quote(body_text)) >= MAILTO_SAFE_LENGTH
        if truncated:
            note = "\n\n[Report shortened. Paste the full report from the clipboard here.]"
            while body_text and len(subject) + len(quote(body_text + note)) >= MAILTO_SAFE_LENGTH:
                body_text = body_text[:-50]
            body_text += note
        if truncated or body_text != full_report:
            self._copy_to_clipboard(full_report)

        url = f"mailto:{FEEDBACK_EMAIL}?subject={subject}&body={quote(body_text)}"
        try:
            open_external(url)
        except Exception:
            self._copy_to_clipboard(f"To: {FEEDBACK_EMAIL}\nSubject: {self._subject()}\n\n{full_report}")
            messagebox.showwarning(
                "Email app not available",
                f"No email app could be opened. The report is copied to the clipboard.\n"
                f"Paste it into an email to {FEEDBACK_EMAIL}.", parent=self)
            return
        message = "Your email app opened with the report. Review it, then select Send."
        if body_text != full_report:
            message += "\n\nThe email holds a shortened version. The full report is on the clipboard."
        messagebox.showinfo("Email ready", message, parent=self)
        self.destroy()


def open_external(target: str) -> None:
    """Open a file, folder or mailto link with the system's default application."""
    if sys.platform.startswith("win"):
        os.startfile(target)  # type: ignore[attr-defined]
        return
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    try:
        # A frozen Linux app sets LD_LIBRARY_PATH to its own libraries; external apps must not inherit it.
        env = dict(os.environ)
        if getattr(sys, "frozen", False):
            original = env.pop("LD_LIBRARY_PATH_ORIG", None)
            if original is not None:
                env["LD_LIBRARY_PATH"] = original
            else:
                env.pop("LD_LIBRARY_PATH", None)
        subprocess.Popen([opener, target], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        if not webbrowser.open(target):
            raise OSError("no application is registered to open this item")


def system_info() -> str:
    lines = [f"App: {APP_NAME} {APP_VERSION}{' (exe)' if getattr(sys, 'frozen', False) else ''}",
             f"OS: {platform.platform()}",
             f"Python: {platform.python_version()}",
             f"PyMuPDF: {getattr(pymupdf, 'VersionBind', getattr(pymupdf, '__version__', 'unknown'))}"]
    try:
        import pymupdf4llm
        lines.append(f"pymupdf4llm: {getattr(pymupdf4llm, '__version__', 'unknown')}")
    except Exception:
        lines.append("pymupdf4llm: not available")
    return "\n".join(lines)


# =============================================================== main window
class PdfOcrApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__(className="grepall")  # Tk reports the window class as "Grepall" (matches the Linux menu entry)
        self.title(f"{APP_NAME} {APP_VERSION}")
        settings = load_settings()
        self.geometry(self._fit_to_screen(settings["window_size"]))
        self.minsize(760, 700)
        self.files: list[Path] = []
        # Each result: (title, OCR PDF, original page numbers, input files)
        self.ocr_results: list[tuple[str, Path, list[int], list[Path]]] = []
        self.messages: queue.Queue = queue.Queue()
        self.cancel = threading.Event()
        self.worker: threading.Thread | None = None
        self.lang = tk.StringVar()
        self.dpi = tk.StringVar()
        self.pages = tk.StringVar()
        self.force = tk.BooleanVar(value=False)
        self.combine_images = tk.BooleanVar()
        self.markers = tk.BooleanVar()
        self.strip_headers = tk.BooleanVar()
        self.arabic_digits = tk.BooleanVar()
        self.arabic_tatweel = tk.BooleanVar()
        self.arabic_diacritics = tk.BooleanVar()
        self.arabic_alef = tk.BooleanVar()
        self.output_dir = tk.StringVar()
        self.status = tk.StringVar(value="Add PDF or image files to begin.")
        self._load_icon()
        self._build()
        self._apply_settings(settings)
        self._refresh_buttons()
        self.after(100, self._poll)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _load_icon(self) -> None:
        self.icon_image = self.header_image = None
        path = resource_path(ICON_FILE)
        if not path.is_file():
            return
        try:
            self.icon_image = tk.PhotoImage(file=str(path))
        except tk.TclError:
            return
        self.iconphoto(True, self.icon_image)  # title bar, taskbar and pop-up windows
        factor = max(1, self.icon_image.height() // 40)  # about 40 px high in the header
        self.header_image = self.icon_image.subsample(factor, factor)

    # ------------------------------------------------------------ settings
    def _fit_to_screen(self, size: str) -> str:
        """Keep the window within the screen, leaving room for the taskbar."""
        width, height = (int(value) for value in size.split("x"))
        width = min(width, self.winfo_screenwidth() - 40)
        height = min(height, self.winfo_screenheight() - 90)
        return f"{max(width, 760)}x{max(height, 700)}"

    def _setting_vars(self) -> dict:
        return {
            "language": self.lang, "quality": self.dpi, "output_dir": self.output_dir,
            "combine_images": self.combine_images, "markers": self.markers,
            "strip_headers": self.strip_headers, "arabic_digits": self.arabic_digits,
            "arabic_tatweel": self.arabic_tatweel, "arabic_diacritics": self.arabic_diacritics,
            "arabic_alef": self.arabic_alef,
        }

    def _apply_settings(self, settings: dict) -> None:
        for key, variable in self._setting_vars().items():
            variable.set(settings[key])
        folder = settings["output_dir"]
        if folder and not Path(folder).is_dir():
            self.output_dir.set("")
            folder = ""
        self.output_label.configure(text=folder or "Same folder as each file")

    def _save_settings(self) -> None:
        settings = {key: variable.get() for key, variable in self._setting_vars().items()}
        if self.state() == "normal":
            settings["window_size"] = f"{self.winfo_width()}x{self.winfo_height()}"
        else:
            settings["window_size"] = load_settings()["window_size"]
        save_settings(settings)

    def reset_settings(self) -> None:
        if not messagebox.askyesno("Reset settings",
                                   "Restore all options to their default values?", parent=self):
            return
        self._apply_settings(DEFAULT_SETTINGS)
        self.geometry(self._fit_to_screen(DEFAULT_SETTINGS["window_size"]))
        try:
            settings_path().unlink()
        except OSError:
            pass
        self._write_log("Settings restored to defaults.")

    def _cleanup_options(self) -> dict:
        return {"digits": self.arabic_digits.get(), "tatweel": self.arabic_tatweel.get(),
                "diacritics": self.arabic_diacritics.get(), "alef": self.arabic_alef.get()}

    # ------------------------------------------------------------ layout
    def _build(self) -> None:
        padding = {"padx": 12, "pady": 6}
        if self.header_image:
            header = ttk.Frame(self, padding=(12, 10, 12, 0))
            header.pack(fill="x")
            ttk.Label(header, image=self.header_image).pack(side="left")
            title_font = tkfont.nametofont("TkDefaultFont").copy()
            title_font.configure(size=14, weight="bold")
            titles = ttk.Frame(header)
            titles.pack(side="left", padx=10)
            ttk.Label(titles, text=APP_NAME, font=title_font).pack(anchor="w")
            ttk.Label(titles, text=APP_TAGLINE, foreground="#555").pack(anchor="w")
        root = ttk.Frame(self)
        root.pack(fill="both", expand=True)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        root.rowconfigure(4, weight=1)

        files = ttk.LabelFrame(root, text="1. Files (PDF or images)")
        files.grid(row=0, column=0, sticky="nsew", **padding)
        files.columnconfigure(0, weight=1)
        files.rowconfigure(0, weight=1)
        self.listbox = tk.Listbox(files, selectmode="extended", height=6, activestyle="none")
        self.listbox.grid(row=0, column=0, sticky="nsew", padx=(8, 0), pady=8)
        scrollbar = ttk.Scrollbar(files, orient="vertical", command=self.listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=8)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        file_buttons = ttk.Frame(files)
        file_buttons.grid(row=0, column=2, sticky="n", padx=8, pady=8)
        self.add_button = ttk.Button(file_buttons, text="Add files...", command=self.add_files)
        self.folder_button = ttk.Button(file_buttons, text="Add folder...", command=self.add_folder)
        self.remove_button = ttk.Button(file_buttons, text="Remove selected", command=self.remove_selected)
        self.clear_button = ttk.Button(file_buttons, text="Clear list", command=self.clear_files)
        for button in (self.add_button, self.folder_button, self.remove_button, self.clear_button):
            button.pack(fill="x", pady=2)

        options = ttk.LabelFrame(root, text="2. Options")
        options.grid(row=1, column=0, sticky="ew", **padding)
        for column in (1, 3):
            options.columnconfigure(column, weight=1)
        ttk.Label(options, text="Document language").grid(row=0, column=0, sticky="w", padx=8, pady=4)
        ttk.Combobox(options, textvariable=self.lang, values=list(LANGUAGES), state="readonly", width=20)\
            .grid(row=0, column=1, sticky="w", pady=4)
        ttk.Label(options, text="Scan quality").grid(row=0, column=2, sticky="w", padx=8, pady=4)
        ttk.Combobox(options, textvariable=self.dpi, values=list(RESOLUTIONS), state="readonly", width=22)\
            .grid(row=0, column=3, sticky="w", pady=4)
        ttk.Label(options, text="Pages (blank = all)").grid(row=1, column=0, sticky="w", padx=8, pady=4)
        ttk.Entry(options, textvariable=self.pages, width=22).grid(row=1, column=1, sticky="w", pady=4)
        ttk.Checkbutton(options, text="OCR pages that already contain text", variable=self.force)\
            .grid(row=1, column=2, columnspan=2, sticky="w", padx=8, pady=4)
        ttk.Label(options, text="Save to").grid(row=2, column=0, sticky="w", padx=8, pady=4)
        output_controls = ttk.Frame(options)
        output_controls.grid(row=2, column=1, columnspan=3, sticky="ew", pady=4, padx=(0, 8))
        output_controls.columnconfigure(0, weight=1)
        self.output_label = ttk.Label(output_controls, text="Same folder as each file", foreground="#555")
        self.output_label.grid(row=0, column=0, sticky="w")
        ttk.Button(output_controls, text="Change...", command=self.choose_output).grid(row=0, column=1, padx=4)
        ttk.Button(output_controls, text="Reset", command=self.reset_output).grid(row=0, column=2)
        ttk.Checkbutton(options, text="Combine images into one PDF", variable=self.combine_images)\
            .grid(row=3, column=0, columnspan=4, sticky="w", padx=8, pady=(0, 6))

        actions = ttk.LabelFrame(root, text="3. Run")
        actions.grid(row=2, column=0, sticky="ew", **padding)
        self.ocr_button = ttk.Button(actions, text="Run OCR", command=self.run_ocr)
        self.markdown_button = ttk.Button(actions, text="Convert to Markdown", command=self.run_markdown)
        self.stop_button = ttk.Button(actions, text="Stop", command=self.stop)
        self.open_button = ttk.Button(actions, text="Open output folder", command=self.open_output)
        self.ocr_button.grid(row=0, column=0, padx=8, pady=8)
        self.markdown_button.grid(row=0, column=1, padx=4, pady=8)
        self.stop_button.grid(row=0, column=2, padx=4, pady=8)
        self.open_button.grid(row=0, column=3, padx=4, pady=8)
        markdown_options = ttk.Frame(actions)
        markdown_options.grid(row=1, column=0, columnspan=4, sticky="w", padx=8, pady=(0, 8))
        ttk.Checkbutton(markdown_options, text="Page markers in Markdown", variable=self.markers).pack(side="left")
        ttk.Checkbutton(markdown_options, text="Remove repeating headers and footers", variable=self.strip_headers)\
            .pack(side="left", padx=16)
        arabic = ttk.Frame(actions)
        arabic.grid(row=2, column=0, columnspan=4, sticky="w", padx=8, pady=(0, 8))
        ttk.Label(arabic, text="Arabic cleanup (Markdown):").grid(row=0, column=0, rowspan=2, sticky="nw", padx=(0, 12))
        for index, (text, variable) in enumerate((
                ("Convert Arabic-Indic digits to 0-9", self.arabic_digits),
                ("Remove stretching (tatweel)", self.arabic_tatweel),
                ("Remove diacritics (tashkeel)", self.arabic_diacritics),
                ("Unify Alef forms", self.arabic_alef))):
            ttk.Checkbutton(arabic, text=text, variable=variable)\
                .grid(row=index // 2, column=1 + index % 2, sticky="w", padx=(0, 16))

        progress = ttk.Frame(root)
        progress.grid(row=3, column=0, sticky="ew", padx=12)
        progress.columnconfigure(0, weight=1)
        self.progress_bar = ttk.Progressbar(progress, mode="determinate")
        self.progress_bar.grid(row=0, column=0, sticky="ew")
        ttk.Label(progress, textvariable=self.status).grid(row=1, column=0, sticky="w", pady=(4, 0))

        log_frame = ttk.LabelFrame(root, text="Activity")
        log_frame.grid(row=4, column=0, sticky="nsew", padx=12, pady=(6, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        self.log = tk.Text(log_frame, height=8, state="disabled", wrap="word")
        self.log.grid(row=0, column=0, sticky="nsew", padx=(8, 0), pady=8)
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log.yview)
        log_scrollbar.grid(row=0, column=1, sticky="ns", pady=8)
        self.log.configure(yscrollcommand=log_scrollbar.set)

        footer = ttk.Frame(root)
        footer.grid(row=5, column=0, sticky="ew", padx=12, pady=(4, 8))
        footer.columnconfigure(2, weight=1)
        ttk.Button(footer, text="Report a bug or suggest an improvement",
                   command=self.open_feedback).grid(row=0, column=0, sticky="w")
        ttk.Button(footer, text="Reset settings", command=self.reset_settings).grid(row=0, column=1, sticky="w", padx=8)
        ttk.Label(footer, text=APP_CREDIT, foreground="#777").grid(row=0, column=3, sticky="e")

    # ------------------------------------------------------------ file list
    def _sync_list(self) -> None:
        self.listbox.delete(0, "end")
        for path in self.files:
            self.listbox.insert("end", str(path))
        self.ocr_results = [result for result in self.ocr_results if any(item in self.files for item in result[3])]
        if not self._busy():
            count = len(self.files)
            self.status.set(f"{count} file{'s' if count != 1 else ''} selected." if count
                            else "Add PDF or image files to begin.")
        self._refresh_buttons()

    def add_files(self) -> None:
        def patterns(suffixes) -> str:  # Linux file dialogs are case-sensitive
            return " ".join(f"*{suffix} *{suffix.upper()}" for suffix in suffixes)
        selected = filedialog.askopenfilenames(title="Select PDF or image files", filetypes=[
            ("PDF and image files", patterns(INPUT_SUFFIXES)),
            ("PDF files", patterns((".pdf",))),
            ("Image files", patterns(IMAGE_SUFFIXES)),
            ("All files", "*")])
        self._add_files([Path(path) for path in selected])

    def add_folder(self) -> None:
        folder = filedialog.askdirectory(title="Select a folder of PDF or image files")
        if folder:
            found = sorted(path for path in Path(folder).iterdir()
                           if path.is_file() and path.suffix.lower() in INPUT_SUFFIXES
                           and not path.stem.endswith(("_ocr", ".partial")))
            if not found:
                messagebox.showinfo("No files found", "The selected folder contains no PDF or image files.")
            self._add_files(found)

    def _add_files(self, paths: list[Path]) -> None:
        for path in paths:
            if path.suffix.lower() in INPUT_SUFFIXES and path not in self.files:
                self.files.append(path)
        self._sync_list()

    def remove_selected(self) -> None:
        for index in reversed(self.listbox.curselection()):
            del self.files[index]
        self._sync_list()

    def clear_files(self) -> None:
        self.files.clear()
        self.ocr_results.clear()
        self._sync_list()

    def choose_output(self) -> None:
        folder = filedialog.askdirectory(title="Select the output folder")
        if folder:
            self.output_dir.set(folder)
            self.output_label.configure(text=folder)

    def reset_output(self) -> None:
        self.output_dir.set("")
        self.output_label.configure(text="Same folder as each file")

    def open_output(self) -> None:
        target = Path(self.output_dir.get()) if self.output_dir.get() else (self.files[0].parent if self.files else None)
        if not target or not target.exists():
            return
        try:
            open_external(str(target))
        except Exception as exc:
            messagebox.showerror("Cannot open folder", f"{target}\n\n{exc}")

    def open_feedback(self) -> None:
        FeedbackDialog(self)

    # ------------------------------------------------------------ state
    def _busy(self) -> bool:
        return bool(self.worker and self.worker.is_alive())

    def _refresh_buttons(self) -> None:
        busy = self._busy()
        idle = "disabled" if busy else "normal"
        for button in (self.add_button, self.folder_button, self.remove_button, self.clear_button):
            button.configure(state=idle)
        self.ocr_button.configure(state="normal" if self.files and not busy else "disabled")
        self.markdown_button.configure(state="normal" if self.ocr_results and not busy else "disabled")
        self.stop_button.configure(state="normal" if busy else "disabled")
        self.open_button.configure(state="normal" if self.files and not busy else "disabled")

    def _write_log(self, text: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def recent_log(self, lines: int) -> str:
        content = self.log.get("1.0", "end").strip().splitlines()
        return "\n".join(content[-lines:])

    def _poll(self) -> None:
        try:
            while True:
                kind, value = self.messages.get_nowait()
                if kind == "log":
                    self._write_log(value)
                elif kind == "status":
                    self.status.set(value)
                elif kind == "bar":
                    done, total = value
                    self.progress_bar.configure(maximum=max(total, 1), value=done)
                elif kind == "result":
                    self.ocr_results.append(value)
                elif kind == "done":
                    if self.worker:
                        self.worker.join(timeout=2)
                    self.worker = None
                    self._refresh_buttons()
                    self.status.set(value)
        except queue.Empty:
            pass
        self.after(100, self._poll)

    def stop(self) -> None:
        self.cancel.set()
        self.status.set("Stopping after the current page...")

    def _on_close(self) -> None:
        if self._busy() and not messagebox.askyesno("Work in progress", "Processing is still running. Stop and close?"):
            return
        self.cancel.set()
        self._save_settings()
        self.destroy()

    def _start(self, target) -> None:
        self.cancel.clear()
        self.worker = threading.Thread(target=target, daemon=True)
        self.worker.start()
        self._refresh_buttons()

    # ------------------------------------------------------------ OCR
    def _plan_jobs(self) -> list[tuple[str, list[Path], Path]] | None:
        """Build (title, inputs, destination) jobs. Returns None if the user cancels."""
        output_dir = self.output_dir.get()
        jobs: list[tuple[str, list[Path], Path]] = []
        used: set[Path] = set()

        def destination_for(source: Path, base_name: str) -> Path:
            folder = Path(output_dir) if output_dir else source.parent
            candidate = folder / f"{base_name}_ocr.pdf"
            if candidate in used:  # e.g. report.pdf and report.jpg in the same run
                candidate = folder / f"{base_name}_{source.suffix.lstrip('.').lower()}_ocr.pdf"
            used.add(candidate)
            return candidate

        images = [path for path in self.files if is_image(path)]
        combine = self.combine_images.get() and len(images) >= 2
        for path in self.files:
            if combine and is_image(path):
                continue
            destination = destination_for(path, path.stem)
            jobs.append((destination.stem[:-4], [path], destination))
        if combine:
            initial_dir = output_dir or str(images[0].parent)
            chosen = filedialog.asksaveasfilename(
                title="Save the combined images as", initialdir=initial_dir,
                initialfile="combined_images_ocr.pdf", defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")], parent=self)
            if not chosen:
                return None
            destination = Path(chosen)
            if destination.suffix.lower() != ".pdf":
                destination = destination.with_suffix(".pdf")
            title = destination.stem[:-4] if destination.stem.endswith("_ocr") else destination.stem
            jobs.append((title, images, destination))
        return jobs

    def run_ocr(self) -> None:
        lang = LANGUAGES[self.lang.get()]
        page_spec = self.pages.get().strip() or None
        try:
            parse_pages(page_spec, 10**6)  # syntax check only
        except ValueError:
            messagebox.showerror("Invalid page selection",
                                 "Enter pages as numbers or ranges, for example: 1-5, 9")
            return
        try:
            tessdata = find_tessdata()
            check_languages(tessdata, lang)
        except Exception as exc:
            messagebox.showerror("Tesseract not ready", str(exc))
            return
        jobs = self._plan_jobs()
        if jobs is None:
            return
        self._save_settings()
        self.ocr_results.clear()
        self._write_log(f"--- OCR started ({self.lang.get()}, {self.dpi.get()}) ---")
        dpi, force = RESOLUTIONS[self.dpi.get()], self.force.get()
        self._start(lambda: self._ocr_worker(jobs, lang, tessdata, dpi, page_spec, force))

    def _ocr_worker(self, jobs: list[tuple[str, list[Path], Path]], lang: str, tessdata: str, dpi: int,
                    page_spec: str | None, force: bool) -> None:
        put = self.messages.put
        completed = 0
        for job_index, (title, inputs, destination) in enumerate(jobs, 1):
            if self.cancel.is_set():
                break
            label = str(inputs[0]) if len(inputs) == 1 else f"{len(inputs)} images combined into {destination.name}"
            put(("log", label))
            started = time.time()
            temp_dir = None
            try:
                destination.parent.mkdir(parents=True, exist_ok=True)
                source = inputs[0]
                if is_image(source):
                    temp_dir = Path(tempfile.mkdtemp(prefix="grepall-"))
                    source = temp_dir / "images.pdf"
                    images_to_pdf(inputs, source)
                with pymupdf.open(source) as probe:
                    page_count = probe.page_count
                try:
                    pages = parse_pages(page_spec, page_count)
                except ValueError:
                    put(("log", f"  Skipped: no selected pages exist in this {page_count}-page file."))
                    continue

                def progress(current: int, total: int, page_number: int, status: str) -> None:
                    put(("bar", (current, total)))
                    put(("status", f"File {job_index} of {len(jobs)}: {destination.name}, "
                                   f"page {page_number} ({current} of {total})"))
                    if "large page" in status:
                        put(("log", f"  Page {page_number}: {status}"))
                    if self.cancel.is_set():
                        raise Cancelled()

                ocr_count, copied_count = ocr_pdf(source, destination, pages, lang, dpi, tessdata, force, progress)
                put(("result", (title, destination, [page + 1 for page in pages], inputs)))
                completed += 1
                put(("log", f"  Saved {destination.name}: {ocr_count} OCR, {copied_count} copied, "
                            f"{time.time() - started:.0f}s"))
            except Cancelled:
                put(("log", "  Stopped. This file was not saved."))
                break
            except Exception as exc:
                put(("log", f"  Failed: {exc}"))
            finally:
                if temp_dir:
                    shutil.rmtree(temp_dir, ignore_errors=True)
        if self.cancel.is_set():
            result = f"Stopped. {completed} file(s) saved."
        else:
            result = f"OCR finished: {completed} of {len(jobs)} file(s) saved."
        if completed:
            result += " Select Convert to Markdown to continue."
        put(("log", result))
        put(("done", result))

    # ------------------------------------------------------------ Markdown
    def run_markdown(self) -> None:
        self._save_settings()
        self._write_log("--- Markdown conversion started ---")
        results, markers, strip = list(self.ocr_results), self.markers.get(), self.strip_headers.get()
        cleanup = self._cleanup_options()
        self._start(lambda: self._markdown_worker(results, markers, strip, cleanup))

    def _markdown_worker(self, results: list[tuple[str, Path, list[int], list[Path]]], markers: bool,
                         strip_headers: bool, cleanup: dict) -> None:
        put = self.messages.put
        completed = 0
        for index, (title, destination, page_numbers, _inputs) in enumerate(results, 1):
            if self.cancel.is_set():
                break
            markdown_path = destination.with_name(f"{title}.md")
            put(("status", f"Converting {destination.name} ({index} of {len(results)})"))
            put(("bar", (index - 1, len(results))))
            try:
                warning = to_markdown(destination, markdown_path, title, page_numbers, markers,
                                      strip_headers, cleanup)
                if warning:
                    put(("log", f"  Note: {warning}"))
                completed += 1
                put(("log", f"  Saved {markdown_path.name}"))
            except Exception as exc:
                put(("log", f"  Failed {destination.name}: {exc}"))
            put(("bar", (index, len(results))))
        if self.cancel.is_set():
            result = f"Stopped. {completed} Markdown file(s) saved."
        else:
            result = f"Markdown finished: {completed} of {len(results)} file(s) saved."
        put(("log", result))
        put(("done", result))

def main() -> None:
    # A windowed .exe has no console: give print() somewhere harmless to write.
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w", encoding="utf-8")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w", encoding="utf-8")
    app = PdfOcrApp()
    try:
        ttk.Style(app).theme_use("vista" if sys.platform.startswith("win") else "clam")
    except tk.TclError:
        pass
    app.mainloop()


if __name__ == "__main__":
    main()
