from datetime import datetime

from pydantic import BaseModel, Field


class ReviewEvidence(BaseModel):
    label: str
    value: str
    source: str | None = None


class ReviewRequest(BaseModel):
    reviewer_decision: str = Field(
        min_length=1,
        max_length=20,
        description="APPROVE, REJECT or ESCALATE.",
    )

    reviewer_comment: str = Field(
        default="",
        max_length=2000,
        description="Optional analyst comment.",
    )


class PendingReviewResponse(BaseModel):
    case_id: str

    risk_level: str | None = None
    priority_score: float | None = None

    human_review_required: bool | None = None

    case_status: str | None = None
    review_status: str | None = None

    reviewer_decision: str | None = None
    reviewer_comment: str | None = None

    reviewed_at: datetime | None = None

    final_status: str | None = None

    # --------------------------------------------------------
    # CASE INFORMATION
    # --------------------------------------------------------

    record_type: str | None = None
    record_id: str | None = None
    invoice_id: str | None = None
    payment_id: str | None = None

    category: str | None = None
    exception_type: str | None = None

    decision: str | None = None
    decision_confidence: float | None = None

    # --------------------------------------------------------
    # FINANCIAL INFORMATION
    # --------------------------------------------------------

    currency: str | None = None

    invoice_amount: float | None = None
    payment_amount: float | None = None
    bank_amount: float | None = None

    payment_fee: float | None = None
    outstanding_amount: float | None = None

    payment_coverage_percent: float | None = None

    invoice_payment_difference: float | None = None
    bank_payment_difference: float | None = None

    financial_status: str | None = None
    financial_impact: str | None = None

    # --------------------------------------------------------
    # AI INVESTIGATION
    # --------------------------------------------------------

    investigation_finding: str | None = None
    likely_cause: str | None = None
    recommended_action: str | None = None

    investigation_confidence: float | None = None

    evidence: list[ReviewEvidence] = []

    reasoning_steps: str | None = None


class ReviewSubmissionResponse(BaseModel):
    case_id: str

    review_status: str

    reviewer_decision: str

    reviewer_comment: str

    reviewed_at: str | None = None

    case_status: str

    final_status: str


class ReviewSummaryResponse(BaseModel):
    total_reviews: int = Field(ge=0)

    pending: int = Field(ge=0)

    completed: int = Field(ge=0)

    approved: int = Field(ge=0)

    rejected: int = Field(ge=0)

    escalated: int = Field(ge=0)