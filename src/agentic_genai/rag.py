from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import tempfile

import fitz


MAX_PDF_SIZE_BYTES = 12 * 1024 * 1024
MAX_EXTRACTED_CHARS = 60_000
MAX_CONTEXT_CHARS = 8_000


@dataclass(frozen=True)
class PdfContext:
    filename: str
    page_count: int
    selected_context: str


def extract_pdf_text(pdf_bytes: bytes) -> tuple[str, int]:
    if not pdf_bytes:
        raise ValueError("Please upload a PDF file.")

    if len(pdf_bytes) > MAX_PDF_SIZE_BYTES:
        raise ValueError("PDF is too large. Please upload a file under 12 MB.")

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_bytes)
        tmp_path = Path(tmp.name)

    try:
        with fitz.open(tmp_path) as document:
            pages = []
            for page_number, page in enumerate(document, start=1):
                page_text = _clean_text(page.get_text("text"))
                if page_text:
                    pages.append(f"[Page {page_number}]\n{page_text}")

            text = "\n\n".join(pages).strip()
            if not text:
                raise ValueError("No readable text was found in the PDF.")

            return text[:MAX_EXTRACTED_CHARS], document.page_count
    finally:
        tmp_path.unlink(missing_ok=True)


def build_pdf_context(pdf_bytes: bytes, filename: str, topic: str) -> PdfContext:
    text, page_count = extract_pdf_text(pdf_bytes)
    chunks = _chunk_text(text)
    selected = _select_relevant_chunks(chunks, topic)

    return PdfContext(
        filename=filename or "uploaded.pdf",
        page_count=page_count,
        selected_context="\n\n".join(selected)[:MAX_CONTEXT_CHARS],
    )


def _clean_text(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _chunk_text(text: str, chunk_size: int = 1_800, overlap: int = 250) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end].strip())
        if end == len(text):
            break
        start = max(end - overlap, start + 1)
    return [chunk for chunk in chunks if chunk]


def _select_relevant_chunks(chunks: list[str], topic: str, limit: int = 5) -> list[str]:
    topic_terms = {
        term.lower()
        for term in re.findall(r"[A-Za-z0-9]{3,}", topic)
        if term.lower() not in {"the", "and", "for", "with", "from"}
    }

    if not topic_terms:
        return chunks[:limit]

    ranked = sorted(
        chunks,
        key=lambda chunk: sum(chunk.lower().count(term) for term in topic_terms),
        reverse=True,
    )
    selected = [chunk for chunk in ranked[:limit] if chunk]
    return selected or chunks[:limit]
