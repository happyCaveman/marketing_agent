from io import BytesIO

from docx import Document
from pypdf import PdfReader


def extract_text(
    content: bytes,
    mime_type: str,
) -> str:
    if mime_type == "application/pdf":
        return _extract_pdf(content)

    if mime_type == (
        "application/vnd.openxmlformats-officedocument."
        "wordprocessingml.document"
    ):
        return _extract_docx(content)

    if mime_type in {
        "text/plain",
        "application/vnd.google-apps.document",
    }:
        return content.decode("utf-8")

    raise ValueError(
        f"Unsupported MIME type: {mime_type}"
    )


def _extract_pdf(content: bytes) -> str:
    reader = PdfReader(BytesIO(content))

    pages = [
        page.extract_text() or ""
        for page in reader.pages
    ]

    return "\n".join(pages)


def _extract_docx(content: bytes) -> str:
    document = Document(BytesIO(content))

    paragraphs = [
        paragraph.text
        for paragraph in document.paragraphs
    ]

    return "\n".join(paragraphs)