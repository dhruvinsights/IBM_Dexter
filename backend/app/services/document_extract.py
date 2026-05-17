"""Extract plain text from uploaded documents (PDF, UTF-8 text)."""

from __future__ import annotations

import logging
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Tuple

logger = logging.getLogger(__name__)


def extract_text_from_bytes(filename: str, raw: bytes, reported_type: str | None = None) -> Tuple[str, str]:
    """Return (text, content_type) for knowledge-base ingestion.

    Raises ValueError if the format is unsupported or no text was extracted.
    """
    ext = Path(filename or "").suffix.lower()
    ctype = (reported_type or "").lower()

    if ext in (".txt", ".md", ".markdown", ".csv", ".json", ".yaml", ".yml") or ctype.startswith("text/"):
        try:
            return raw.decode("utf-8"), ctype or "text/plain"
        except UnicodeDecodeError as exc:
            raise ValueError("File must be UTF-8 for this type.") from exc

    if ext == ".pdf" or ctype == "application/pdf":
        return _extract_pdf(raw), "application/pdf"

    # .docx is a zip of XML
    if ext == ".docx" or ctype in ("application/vnd.openxmlformats-officedocument.wordprocessingml.document",):
        return _extract_docx(raw), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    # Default: try utf-8 decode (code files etc.)
    try:
        return raw.decode("utf-8"), ctype or "text/plain"
    except UnicodeDecodeError as exc:
        raise ValueError(
            "Unsupported or binary file. Upload PDF, DOCX, or UTF-8 text/markdown/code."
        ) from exc


def _extract_pdf(raw: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ValueError("PDF support requires the pypdf package.") from exc

    reader = PdfReader(BytesIO(raw))
    parts: list[str] = []
    for page in reader.pages:
        try:
            t = page.extract_text() or ""
        except Exception as exc:  # noqa: BLE001
            logger.warning("PDF page extract failed: %s", exc)
            t = ""
        if t.strip():
            parts.append(t)
    text = "\n\n".join(parts).strip()
    if not text:
        raise ValueError("No extractable text in PDF (scanned images are not OCR'd).")
    return text


def _extract_docx(raw: bytes) -> str:
    try:
        from xml.etree import ElementTree
    except ImportError as exc:
        raise ValueError("Cannot read DOCX.") from exc

    try:
        with zipfile.ZipFile(BytesIO(raw)) as zf:
            xml = zf.read("word/document.xml")
    except (KeyError, zipfile.BadZipFile) as exc:
        raise ValueError("Invalid DOCX file.") from exc

    tree = ElementTree.fromstring(xml)
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs: list[str] = []
    for p in tree.findall(".//w:p", ns):
        runs = [t.text for t in p.findall(".//w:t", ns) if t.text]
        line = "".join(runs).strip()
        if line:
            paragraphs.append(line)
    text = "\n".join(paragraphs).strip()
    if not text:
        raise ValueError("No text found in DOCX.")
    return text
