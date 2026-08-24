from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

Onset = Literal["sudden", "gradual"]


class SymptomCreate(BaseModel):
    session_id: str = Field(min_length=8, max_length=64)
    primary_symptoms: list[str] = Field(min_length=1, max_length=15)
    description: str = Field(default="", max_length=4000)
    duration_text: str = Field(default="", max_length=128)
    severity: int = Field(ge=1, le=10)
    onset: Onset
    additional_symptoms: list[str] = Field(default_factory=list, max_length=20)

    @field_validator("primary_symptoms", "additional_symptoms", mode="before")
    @classmethod
    def split_csv(cls, value):
        if isinstance(value, str):
            return [part.strip() for part in value.split(",") if part.strip()]
        return value

    @field_validator("primary_symptoms", "additional_symptoms")
    @classmethod
    def clean_items(cls, value: list[str]) -> list[str]:
        cleaned = []
        for item in value:
            text = item.strip()
            if not text:
                raise ValueError("Symptom entries cannot be empty.")
            if len(text) > 120:
                raise ValueError("Each symptom entry must be 120 characters or fewer.")
            cleaned.append(text)
        return cleaned


class SymptomRead(BaseModel):
    id: int
    primary_symptoms: list[str]
    description: str
    duration_text: str
    severity: int
    onset: Onset
    additional_symptoms: list[str]
    created_at: datetime

    model_config = {"from_attributes": True}
