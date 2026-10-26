"""Safe, local text extraction for presentation-ready document ingestion."""

from __future__ import annotations

import io
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree

from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}
MAX_FILE_BYTES = 12 * 1024 * 1024


class IngestionError(ValueError):
    pass


def _clean(text: str) -> str:
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _extract_pdf(content: bytes) -> tuple[str, int]:
    try:
        reader = PdfReader(io.BytesIO(content))
        pages = [(page.extract_text() or "").strip() for page in reader.pages]
    except Exception as exc:  # pypdf raises several parser-specific exceptions
        raise IngestionError("The PDF could not be parsed. Try a text-based, non-encrypted PDF.") from exc
    text = _clean("\n\n".join(page for page in pages if page))
    if not text:
        raise IngestionError("No selectable text was found. Scanned PDFs require OCR before ingestion.")
    return text, len(reader.pages)


def _extract_docx(content: bytes) -> tuple[str, int]:
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            xml = archive.read("word/document.xml")
        root = ElementTree.fromstring(xml)
    except (KeyError, zipfile.BadZipFile, ElementTree.ParseError) as exc:
        raise IngestionError("The DOCX file is invalid or damaged.") from exc
    namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    paragraphs = []
    for paragraph in root.iter(f"{namespace}p"):
        value = "".join(node.text or "" for node in paragraph.iter(f"{namespace}t")).strip()
        if value:
            paragraphs.append(value)
    text = _clean("\n".join(paragraphs))
    if not text:
        raise IngestionError("No readable paragraphs were found in the DOCX file.")
    return text, 1


def extract_document(filename: str, content: bytes) -> dict[str, object]:
    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise IngestionError("Supported formats are PDF, DOCX, TXT, and Markdown.")
    if not content:
        raise IngestionError("The uploaded document is empty.")
    if len(content) > MAX_FILE_BYTES:
        raise IngestionError("The document exceeds the 12 MB presentation limit.")
    if extension == ".pdf":
        text, page_count = _extract_pdf(content)
    elif extension == ".docx":
        text, page_count = _extract_docx(content)
    else:
        try:
            text = _clean(content.decode("utf-8-sig"))
        except UnicodeDecodeError as exc:
            raise IngestionError("Text files must use UTF-8 encoding.") from exc
        page_count = 1
    if len(text) > 250_000:
        raise IngestionError("Extracted text exceeds the 250,000-character analysis limit.")
    return {
        "filename": Path(filename).name,
        "format": extension.removeprefix(".").upper(),
        "text": text,
        "characters": len(text),
        "words": len(re.findall(r"\S+", text)),
        "pages": page_count,
    }
