import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models import AnalysisSession, HealthProfile
from app.schemas.analysis import SessionBundle
from app.schemas.health_profile import HealthProfileCreate, HealthProfileRead

router = APIRouter(prefix="/api", tags=["profile"])


@router.post("/profile", response_model=SessionBundle, status_code=201)
def create_profile(payload: HealthProfileCreate, db: Session = Depends(get_db)) -> SessionBundle:
    profile = HealthProfile(
        age=payload.age,
        sex=payload.sex,
        conditions=[c.strip()[:200] for c in payload.conditions if c.strip()],
        allergies=[a.strip()[:200] for a in payload.allergies if a.strip()],
        medications=[m.strip()[:200] for m in payload.medications if m.strip()],
        history=(payload.history or "").strip() or None,
    )
    db.add(profile)
    db.flush()

    session = AnalysisSession(id=uuid.uuid4().hex, profile_id=profile.id, status="created")
    db.add(session)
    db.commit()
    db.refresh(profile)
    return SessionBundle(profile_id=profile.id, session_id=session.id)


@router.get("/profile/{profile_id}", response_model=HealthProfileRead)
def get_profile(profile_id: int, db: Session = Depends(get_db)) -> HealthProfileRead:
    profile = db.get(HealthProfile, profile_id)
    if profile is None:
        from app.core.errors import NotFoundError

        raise NotFoundError("Health profile not found.")
    return profile
