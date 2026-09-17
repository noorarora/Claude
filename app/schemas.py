from datetime import datetime

from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    text: str = Field(min_length=10, max_length=10_000)


class Signal(BaseModel):
    label: str
    detail: str
    severity: str


class AnalysisResponse(BaseModel):
    id: int
    risk_score: int = Field(ge=0, le=100)
    verdict: str
    confidence: float = Field(ge=0, le=1)
    signals: list[Signal]
    recommendation: str
    created_at: datetime


class HistoryItem(BaseModel):
    id: int
    preview: str
    risk_score: int
    verdict: str
    created_at: datetime

