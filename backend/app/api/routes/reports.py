from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_provider, get_settings_dep
from app.core.config import Settings
from app.core.errors import NotFoundError
from app.models import Report
from app.schemas.reports import ReportDetail, ReportExplanationOut, ReportFindings, ReportRead, UploadResponse
from app.services.ai.base import AIProvider
from app.services.reports.service import save_report

router = APIRouter(prefix="/api", tags=["reports"])

UNREADABLE_MESSAGE = (
    "This report could not be read automatically, so no explanation can be provided. "
    "Please review the document directly with a healthcare professional."
)


def _get_report_or_404(db: Session, report_id: int) -> Report:
    report = db.get(Report, report_id)
    if report is None:
        raise NotFoundError("Report not found.")
    return report


@router.post("/reports/upload", response_model=UploadResponse)
def upload_report(
    session_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> UploadResponse:
    report, message = save_report(db, session_id, file)
    return UploadResponse(report=ReportRead.model_validate(report), message=message)


@router.get("/reports/{report_id}", response_model=ReportDetail)
def get_report(report_id: int, db: Session = Depends(get_db)) -> ReportDetail:
    return ReportDetail(report=ReportRead.model_validate(_get_report_or_404(db, report_id)))


@router.post("/reports/{report_id}/explain", response_model=ReportExplanationOut)
def explain_report(
    report_id: int,
    db: Session = Depends(get_db),
    provider: AIProvider = Depends(get_provider),
    settings: Settings = Depends(get_settings_dep),
) -> ReportExplanationOut:
    report = _get_report_or_404(db, report_id)

    if report.status == "stored_no_ocr":
        return ReportExplanationOut(
            explanation=(
                "This image was stored but OCR is not enabled in this prototype, so its contents "
                "cannot be explained. Please consult a healthcare professional for interpretation."
            ),
            demo_mode=settings.is_demo_mode,
        )
    if report.status != "parsed":
        return ReportExplanationOut(explanation=UNREADABLE_MESSAGE, demo_mode=settings.is_demo_mode)

    findings = (
        ReportFindings.model_validate(report.extracted_findings)
        if report.extracted_findings
        else None
    )
    explanation = provider.explain_medical_report(report.raw_text or "", findings)
    return ReportExplanationOut(explanation=explanation, demo_mode=settings.is_demo_mode)
