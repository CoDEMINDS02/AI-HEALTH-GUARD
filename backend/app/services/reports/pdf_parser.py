import io

from pypdf import PdfReader

from app.core.errors import FileProcessingError


def extract_pdf_text(file_bytes: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        pages = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            pages.append(page_text)
        text = "\n".join(pages).strip()
    except FileProcessingError:
        raise
    except Exception as exc:
        raise FileProcessingError(
            "The PDF could not be read. It may be corrupted or password-protected.",
            code="pdf_extraction_failed",
        ) from exc

    if not text:
        raise FileProcessingError(
            "No readable text was found in this PDF. It is likely a scanned image, which this "
            "prototype cannot process without OCR.",
            code="pdf_text_extraction_empty",
        )
    return text
