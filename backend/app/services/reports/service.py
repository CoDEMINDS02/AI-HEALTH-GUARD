from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import FileProcessingError, NotFoundError
from app.models import AnalysisSession, Report
from app.schemas.reports import ReportFindings
from app.services.reports.normalizer import normalize_report
from app.services.reports.pdf_parser import extract_pdf_text

PDF_SUFFIXES = {".pdf"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}

OCR_NOTE = (
    "Image stored. Text extraction (OCR) is not enabled in this prototype, so no values were "
    "read from the image."
)


def get_session_or_404(db: Session, session_id: str) -> AnalysisSession:
    session = db.get(AnalysisSession, session_id)
    if session is None:
        raise NotFoundError("Analysis session not found.")
    return session


def _validate_upload(upload: UploadFile) -> tuple[str, bytes]:
    settings = get_settings()
    filename = (upload.filename or "upload").strip()
    suffix = ("." + filename.rsplit(".", 1)[-1].lower()) if "." in filename else ""

    if suffix not in PDF_SUFFIXES | IMAGE_SUFFIXES:
        raise FileProcessingError(
            "Unsupported file type. Please upload a PDF or an image (PNG/JPG/WEBP).",
            code="unsupported_file_type",
        )

    data = upload.file.read()
    if len(data) == 0:
        raise FileProcessingError("The uploaded file is empty.", code="empty_file")
    if len(data) > settings.upload_max_bytes:
        raise FileProcessingError("The uploaded file is too large.", code="file_too_large", status_code=413)
    if suffix in PDF_SUFFIXES and not data.startswith(b"%PDF"):
        raise FileProcessingError(
            "This file does not look like a valid PDF.", code="invalid_pdf_file"
        )
    return suffix.lstrip("."), data


def save_report(db: Session, session_id: str, upload: UploadFile) -> tuple[Report, str]:
    session = get_session_or_404(db, session_id)
    file_type, data = _validate_upload(upload)

    findings_payload = None
    notes = None

    if file_type == "pdf":
        try:
            text = extract_pdf_text(data)
            normalized = normalize_report(text)
            findings_payload = normalized.model_dump()
            raw_text = text[:20000]
        except FileProcessingError as exc:
            report = Report(
                session_id=session.id,
                filename=upload.filename or "report.pdf",
                file_type="pdf",
                status="extraction_failed",
                raw_text=None,
                extracted_findings=None,
                notes=str(exc),
            )
            db.add(report)
            db.commit()
            db.refresh(report)
            return report, str(exc)
    else:
        report = Report(
            session_id=session.id,
            filename=upload.filename or "image",
            file_type=file_type,
            status="stored_no_ocr",
            raw_text=None,
            extracted_findings=None,
            notes=OCR_NOTE,
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report, OCR_NOTE

    report = Report(
        session_id=session.id,
        filename=upload.filename or "report.pdf",
        file_type="pdf",
        status="parsed",
        raw_text=raw_text,
        extracted_findings=findings_payload,
        notes=None,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    message = "Report parsed successfully."
    if findings_payload:
        findings = ReportFindings.model_validate(findings_payload)
        message = f"Extracted {len(findings.findings)} value(s) from the report."
    return report, message
