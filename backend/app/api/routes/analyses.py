from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_provider
from app.schemas.analysis import AnalysisRead, AnalysisSummaryItem, AnalyzeIn
from app.services.ai.base import AIProvider
from app.services.analysis.orchestrator import get_result_or_404, run_analysis

router = APIRouter(prefix="/api", tags=["analyses"])


@router.post("/analyze", response_model=AnalysisRead)
def analyze(payload: AnalyzeIn, db: Session = Depends(get_db), provider: AIProvider = Depends(get_provider)):
    result = run_analysis(db, payload.session_id, provider)
    return result


@router.get("/analyses", response_model=list[AnalysisSummaryItem])
def list_analyses(
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list:
    from app.models import AnalysisResult

    return (
        db.query(AnalysisResult)
        .order_by(AnalysisResult.id.desc())
        .limit(limit)
        .all()
    )


@router.get("/analyses/{analysis_id}", response_model=AnalysisRead)
def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    return get_result_or_404(db, analysis_id)
