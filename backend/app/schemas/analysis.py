from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

RiskLevel = Literal["LOW", "MODERATE", "HIGH"]


def _clean_str_list(value: list[str]) -> list[str]:
    cleaned = []
    for item in value:
        text = item.strip() if isinstance(item, str) else ""
        if text:
            cleaned.append(text[:600])
    return cleaned


class AnalysisResultSchema(BaseModel):
    """Contract for AI output. Every provider must produce data that validates here."""

    summary: str = Field(min_length=1)
    symptoms: list[str] = Field(default_factory=list)
    observations: list[str] = Field(default_factory=list)
    possible_concerns: list[str] = Field(default_factory=list)
    risk_level: RiskLevel
    red_flags: list[str] = Field(default_factory=list)
    recommended_next_steps: list[str] = Field(default_factory=list)
    questions_for_doctor: list[str] = Field(default_factory=list)
    limitations: str = ""
    disclaimer: str = ""
    safety_override: bool = False

    @field_validator(
        "symptoms",
        "observations",
        "possible_concerns",
        "red_flags",
        "recommended_next_steps",
        "questions_for_doctor",
        mode="before",
    )
    @classmethod
    def coerce_lists(cls, value):
        if isinstance(value, str):
            return [value]
        if isinstance(value, dict):
            value = [value]
        if isinstance(value, list):
            normalized = []
            for item in value:
                if isinstance(item, str):
                    normalized.append(item)
                elif isinstance(item, dict):
                    text = item.get("title") or item.get("name") or item.get("text")
                    if not text and item:
                        text = "; ".join(f"{k}: {v}" for k, v in item.items())
                    if text:
                        normalized.append(str(text))
            return normalized
        return value

    @field_validator(
        "symptoms",
        "observations",
        "possible_concerns",
        "red_flags",
        "recommended_next_steps",
        "questions_for_doctor",
    )
    @classmethod
    def clean(cls, value: list[str]) -> list[str]:
        return _clean_str_list(value)

    @model_validator(mode="after")
    def fill_defaults(self) -> "AnalysisResultSchema":
        from app.core.constants import DEFAULT_LIMITATIONS_TEXT, DISCLAIMER_TEXT

        if not self.limitations:
            self.limitations = DEFAULT_LIMITATIONS_TEXT
        if not self.disclaimer:
            self.disclaimer = DISCLAIMER_TEXT
        return self


class AnalyzeIn(BaseModel):
    session_id: str = Field(min_length=8, max_length=64)


class AnalysisRead(BaseModel):
    id: int
    session_id: str
    summary: str
    symptoms: list[str]
    observations: list[str]
    possible_concerns: list[str]
    risk_level: RiskLevel
    red_flags: list[str]
    recommended_next_steps: list[str]
    questions_for_doctor: list[str]
    limitations: str
    disclaimer: str
    source: str
    safety_override: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisSummaryItem(BaseModel):
    id: int
    session_id: str
    risk_level: RiskLevel
    summary: str
    created_at: datetime
    safety_override: bool

    model_config = {"from_attributes": True}


class SessionBundle(BaseModel):
    profile_id: int
    session_id: str
