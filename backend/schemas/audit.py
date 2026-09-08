from datetime import datetime

from pydantic import BaseModel


class AuditEventResponse(BaseModel):
    id: int
    case_id: str
    previous_status: str | None = None
    new_status: str
    changed_by: str | None = None
    action: str
    reason: str | None = None
    timestamp: datetime


class AuditTrailResponse(BaseModel):
    case_id: str
    current_status: str
    total_events: int
    events: list[AuditEventResponse]