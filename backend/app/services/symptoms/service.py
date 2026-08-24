from sqlalchemy.orm import Session

from app.models import AnalysisSession, SymptomInput
from app.schemas.symptoms import SymptomCreate


def create_symptom_input(db: Session, session: AnalysisSession, data: SymptomCreate) -> SymptomInput:
    record = SymptomInput(
        session_id=session.id,
        primary_symptoms=data.primary_symptoms,
        description=data.description,
        duration_text=data.duration_text,
        severity=data.severity,
        onset=data.onset,
        additional_symptoms=data.additional_symptoms,
    )
    db.add(record)
    session.status = "symptoms_recorded"
    db.commit()
    db.refresh(record)
    return record


def get_latest_symptom_context(db: Session, session: AnalysisSession) -> dict | None:
    latest = (
        db.query(SymptomInput)
        .filter(SymptomInput.session_id == session.id)
        .order_by(SymptomInput.id.desc())
        .first()
    )
    if latest is None:
        return None
    return {
        "primary_symptoms": latest.primary_symptoms or [],
        "additional_symptoms": latest.additional_symptoms or [],
        "description": latest.description or "",
        "duration_text": latest.duration_text or "",
        "severity": latest.severity,
        "onset": latest.onset,
    }
