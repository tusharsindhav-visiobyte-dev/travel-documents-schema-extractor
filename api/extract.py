"""Turn an upload into plain text."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from api.errors import DocumentInputError, UnsupportedFileError

_TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".json", ".html", ".htm", ".xml", ".text"}
_TEXT_MEDIA_TYPES = {"application/json", "application/xml", "application/xhtml+xml"}


def extract_upload(
    filename: str | None,
    content_type: str | None,
    data: bytes,
    *,
    max_bytes: int,
) -> str:
    """Read text from a plain-text upload or a PDF."""
    if len(data) > max_bytes:
        raise DocumentInputError(f"File exceeds the {max_bytes} byte limit.")
    if not data:
        raise DocumentInputError("The uploaded file is empty.")

    suffix = Path(filename or "").suffix.lower()
    media = (content_type or "").split(";")[0].strip().lower()
    if media.startswith("image/"):
        raise UnsupportedFileError("Image files are not read. Paste the document text instead.")
    if suffix == ".pdf" or media == "application/pdf" or data.startswith(b"%PDF"):
        return _pdf_text(data)
    if suffix in _TEXT_EXTENSIONS or media.startswith("text/") or media in _TEXT_MEDIA_TYPES or _looks_like_text(data):
        return _decode_text(data)
    raise UnsupportedFileError("Upload a text file or a PDF, or send the document as text.")


def _decode_text(data: bytes) -> str:
    text = data.decode("utf-8", errors="replace").strip()
    if not text:
        raise DocumentInputError("The uploaded file has no text.")
    return text


def _looks_like_text(data: bytes) -> bool:
    sample = data[:2048]
    if b"\x00" in sample:
        return False
    printable = sum(byte in b"\t\r\n" or 32 <= byte < 127 for byte in sample)
    return printable / len(sample) > 0.9


def _pdf_text(data: bytes) -> str:
    try:
        from pypdf import PdfReader
        from pypdf.errors import PdfReadError
    except ImportError as exc:  # pragma: no cover - dependency is installed with the app
        raise DocumentInputError("PDF support is not installed.") from exc

    try:
        reader = PdfReader(stream=BytesIO(data))
    except (PdfReadError, OSError, ValueError) as exc:
        raise DocumentInputError("The PDF could not be read.") from exc

    pages: list[str] = []
    for page in reader.pages[:20]:
        extracted = page.extract_text() or ""
        if extracted.strip():
            pages.append(extracted)
    text = "\n".join(pages).strip()
    if not text:
        raise DocumentInputError("The PDF has no extractable text. Paste the document text instead.")
    return text
