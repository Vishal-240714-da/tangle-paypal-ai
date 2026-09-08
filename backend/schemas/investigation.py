from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InvestigationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int

    case_id: str

    finding: str | None = None
    likely_cause: str | None = None
    recommendation: str | None = None

    confidence: float | None = None
    evidence: str | None = None

    created_at: datetime | None = None