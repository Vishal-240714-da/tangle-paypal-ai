from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# CASE RESPONSE
# ============================================================

class CaseResponse(BaseModel):
    """
    API response model for a single TANGLE case.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    case_id: str

    record_type: str | None = None
    record_id: str | None = None
    invoice_id: str | None = None

    category: str | None = None
    confidence: float | None = None

    suggested_action: str | None = None
    reason: str | None = None
    next_action: str | None = None

    payment_amount: float | None = None
    bank_amount: float | None = None
    payment_fee: float | None = None

    outstanding_amount: float | None = None
    payment_coverage_percent: float | None = None

    bank_payment_difference: float | None = None
    invoice_payment_difference: float | None = None

    financial_status: str | None = None
    financial_impact: str | None = None

    original_invoice_amount: float | None = None

    decision: str | None = None
    decision_confidence: float | None = None

    related_invoice_count: int | None = None
    related_invoice_ids: str | None = None

    # --------------------------------------------------------
    # Phase 2 lifecycle fields
    # --------------------------------------------------------

    status: str | None = None
    risk_level: str | None = None
    priority_score: float | None = None
    human_review_required: bool | None = None

    # --------------------------------------------------------
    # Timestamps
    # --------------------------------------------------------

    created_at: datetime | None = None
    updated_at: datetime | None = None


# ============================================================
# CASE LIST RESPONSE
# ============================================================

class CaseListResponse(BaseModel):
    """
    Paginated API response for TANGLE cases.
    """

    items: list[CaseResponse]

    total: int = Field(
        ge=0
    )

    page: int = Field(
        ge=1
    )

    page_size: int = Field(
        ge=1
    )

    total_pages: int = Field(
        ge=0
    )


# ============================================================
# CASE HISTORY RESPONSE
# ============================================================

class CaseHistoryResponse(BaseModel):
    """
    API response for a TANGLE case lifecycle
    and audit-history record.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    case_id: str

    previous_status: str | None = None

    new_status: str

    changed_by: str | None = None

    reason: str | None = None

    timestamp: datetime