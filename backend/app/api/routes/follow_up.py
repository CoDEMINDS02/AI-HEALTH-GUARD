from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_settings_dep, get_provider
from app.core.config import Settings
from app.core.errors import InvalidStateError
from app.schemas.analysis import SessionBundle
from app.schemas.follow_up import FollowUpAnswersIn, FollowUpGenerateIn, FollowUpQuestionsOut
from app.models import AnalysisSession
from app.services.ai.base import AIProvider
from app.services.reports.service import get_session_or_404
from app.services.symptoms.service import get_latest_symptom_context

router = APIRouter(prefix="/api", tags=["follow-up"])


@router.post("/follow-up", response_model=FollowUpQuestionsOut)
def generate_follow_up(
    payload: FollowUpGenerateIn,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
    provider: AIProvider = Depends(get_provider),
) -> FollowUpQuestionsOut:
    session = get_session_or_404(db, payload.session_id)
    context = get_latest_symptom_context(db, session)
    if context is None:
        raise InvalidStateError("Add your symptoms before generating follow-up questions.")

    context["max_questions"] = max(2, min(6, settings.ai_max_follow_up_questions))
    questions = provider.generate_follow_up_questions(context)[: context["max_questions"]]

    session.follow_up_questions = questions
    session.status = "follow_up_pending"
    db.commit()
    return FollowUpQuestionsOut(
        session_id=session.id,
        questions=questions,
        demo_mode=settings.is_demo_mode,
    )


@router.post("/follow-up/answers", response_model=SessionBundle)
def submit_follow_up_answers(payload: FollowUpAnswersIn, db: Session = Depends(get_db)):
    session = db.get(AnalysisSession, payload.session_id)
    if session is None:
        from app.core.errors import NotFoundError

        raise NotFoundError("Analysis session not found.")
    session.follow_up_answers = [
        {"question": a.question, "answer": a.answer} for a in payload.answers
    ]
    session.status = "follow_up_complete"
    db.commit()
    return SessionBundle(profile_id=session.profile_id, session_id=session.id)


__all__ = ["SessionBundle"]
