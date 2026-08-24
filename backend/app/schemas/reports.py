from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

FindingFlag = Literal["normal", "high", "low", "abnormal", "unknown"]


class LabFinding(BaseModel):
    name: str
    value: str
    numeric_value: float | None = None
    unit: str | None = None
    reference_range: str | None = None
    flag: FindingFlag = "unknown"


class ReportFindings(BaseModel):
    findings: list[LabFinding] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    summary: str = ""
    extraction_status: Literal["parsed", "failed", "not_applicable"] = "parsed"


class ReportRead(BaseModel):
    id: int
    session_id: str
    filename: str
    file_type: str
    status: str
    extracted_findings: ReportFindings | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class UploadResponse(BaseModel):
    report: ReportRead
    message: str


class ReportDetail(BaseModel):
    report: ReportRead


class ReportExplanationOut(BaseModel):
    explanation: str
    demo_mode: bool
