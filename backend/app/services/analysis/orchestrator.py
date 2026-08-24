from sqlalchemy.orm import Session

from app.core.constants import DISCLAIMER_TEXT, DEFAULT_LIMITATIONS_TEXT
from app.core.errors import AIProviderError, InvalidStateError, NotFoundError
from app.core.logging import get_logger
from app.models import AnalysisResult, AnalysisSession, Report
from app.schemas.analysis import AnalysisResultSchema  # noqa: F401 (re-exported contract)
from app.services.ai.base import AIProvider
from app.services.reports.service import get_session_or_404
from app.services.risk.engine import apply_safety_layer
from app.services.risk.red_flags import assess_text_safety
from app.services.symptoms.service import get_latest_symptom_context

logger = get_logger(__name__)


def build_analysis_payload(db: Session, session: AnalysisSession) -> dict:
    profile = session.profile
    symptom_context = get_latest_symptom_context(db, session)
    if symptom_context is None:
        raise InvalidStateError("Add your symptoms before requesting an analysis.")

    report_row = (
        db.query(Report).filter(Report.session_id == session.id).order_by(Report.id.desc()).first()
    )

    return {
        "health_profile": {
            "age": profile.age,
            "sex": profile.sex,
            "known_conditions": profile.conditions or [],
            "allergies": profile.allergies or [],
            "current_medications": profile.medications or [],
            "relevant_history": (profile.history or "")[:1000],
        },
        "symptoms": symptom_context,
        "follow_up_answers": [
            {"question": a.get("question", ""), "answer": a.get("answer", "")}
            for a in (session.follow_up_answers or [])
            if isinstance(a, dict) and a.get("answer")
        ],
        "medical_report_findings": report_row.extracted_findings if report_row else None,
    }


def run_analysis(db: Session, session_id: str, provider: AIProvider) -> AnalysisResult:
    session = get_session_or_404(db, session_id)

    payload = build_analysis_payload(db, session)
    try:
        analysis = provider.analyze_health_information(payload)
    except AIProviderError:
        raise
    except Exception as exc:
        logger.exception("AI analysis failed unexpectedly")
        raise AIProviderError("The health analysis could not be completed. Please try again.") from exc

    assessment = assess_text_safety(
        payload["symptoms"].get("description"),
        " ".join(payload["symptoms"].get("primary_symptoms", [])),
        " ".join(payload["symptoms"].get("additional_symptoms", [])),
        *[a.get("answer", "") for a in payload["follow_up_answers"]],
    )
    final = apply_safety_layer(analysis, assessment)
    final.disclaimer = final.disclaimer or DISCLAIMER_TEXT
    final.limitations = final.limitations or DEFAULT_LIMITATIONS_TEXT

    result = AnalysisResult(
        session_id=session.id,
        summary=final.summary,
        symptoms=final.symptoms,
        observations=final.observations,
        possible_concerns=final.possible_concerns,
        risk_level=final.risk_level,
        red_flags=final.red_flags,
        recommended_next_steps=final.recommended_next_steps,
        questions_for_doctor=final.questions_for_doctor,
        limitations=final.limitations,
        disclaimer=final.disclaimer,
        source=provider.name,
        safety_override=final.safety_override,
    )
    db.add(result)
    session.status = "analyzed"
    db.commit()
    db.refresh(result)

    logger.info(
        "Analysis %s completed | risk=%s override=%s provider=%s",
        result.id,
        result.risk_level,
        result.safety_override,
        provider.name,
    )
    return result


def get_result_or_404(db: Session, analysis_id: int) -> AnalysisResult:
    result = db.get(AnalysisResult, analysis_id)
    if result is None:
        raise NotFoundError("Analysis not found.")
    return result
