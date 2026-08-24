from abc import ABC, abstractmethod

from app.schemas.analysis import AnalysisResultSchema
from app.schemas.reports import ReportFindings


class AIProvider(ABC):
    """Abstraction over LLM backends so vendors can be swapped without touching app logic."""

    name: str = "base"

    def __init__(self, settings=None) -> None:
        self.settings = settings

    @abstractmethod
    def generate_follow_up_questions(self, symptom_context: dict) -> list[str]:
        """Return a small set of relevant follow-up questions for the given symptoms."""

    @abstractmethod
    def analyze_health_information(self, payload: dict) -> AnalysisResultSchema:
        """Return a validated structured assessment for the combined user data."""

    @abstractmethod
    def explain_medical_report(self, report_text: str, findings: ReportFindings | None) -> str:
        """Return a plain-language explanation of an uploaded medical report."""
