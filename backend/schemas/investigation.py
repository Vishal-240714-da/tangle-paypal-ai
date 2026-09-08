from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InvestigationEvidence(BaseModel):
    label: str
    value: str
    source: str | None = None


class InvestigationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_id: str

    finding: str | None = None
    likely_cause: str | None = None
    recommendation: str | None = None

    confidence: float | None = None

    evidence: list[InvestigationEvidence] = []

    created_at: datetime | None = None