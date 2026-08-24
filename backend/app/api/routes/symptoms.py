from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.symptoms import SymptomCreate
from app.services.reports.service import get_session_or_404
from app.services.symptoms.service import create_symptom_input

router = APIRouter(prefix="/api", tags=["symptoms"])


@router.post("/symptoms", status_code=201)
def submit_symptoms(payload: SymptomCreate, db: Session = Depends(get_db)) -> dict:
    session = get_session_or_404(db, payload.session_id)
    record = create_symptom_input(db, session, payload)
    return {
        "session_id": session.id,
        "recorded": 1,
        "severity": record.severity,
        "status": session.status,
    }
