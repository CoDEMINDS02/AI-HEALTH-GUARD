from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Sex = Literal["male", "female", "other", "prefer_not_to_say"]


class HealthProfileCreate(BaseModel):
    age: int = Field(ge=0, le=120)
    sex: Sex
    conditions: list[str] = Field(default_factory=list, max_length=30)
    allergies: list[str] = Field(default_factory=list, max_length=30)
    medications: list[str] = Field(default_factory=list, max_length=50)
    history: str | None = Field(default=None, max_length=2000)


class HealthProfileRead(BaseModel):
    id: int
    age: int
    sex: Sex
    conditions: list[str]
    allergies: list[str]
    medications: list[str]
    history: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
