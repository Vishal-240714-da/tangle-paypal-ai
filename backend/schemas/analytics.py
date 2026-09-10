from pydantic import BaseModel, Field


class HumanReviewMetrics(BaseModel):
    required: int = Field(ge=0)
    not_required: int = Field(ge=0)
    rate: float = Field(ge=0)


class FinancialMetrics(BaseModel):
    outstanding_balance: float
    average_payment_coverage: float
    total_invoice_amount: float
    total_payment_amount: float
    total_bank_amount: float


class PriorityMetrics(BaseModel):
    average: float
    maximum: float
    minimum: float


class ReviewOutcomeMetrics(BaseModel):
    approved: int = Field(ge=0)
    rejected: int = Field(ge=0)
    escalated: int = Field(ge=0)
    pending: int = Field(ge=0)
    completion_rate: float = Field(ge=0)


class AnalyticsSummaryResponse(BaseModel):
    # Existing analytics
    risk_distribution: dict[str, int]
    exception_distribution: dict[str, int]
    lifecycle_distribution: dict[str, int]
    decision_distribution: dict[str, int]

    # Human governance
    human_review: HumanReviewMetrics
    review_outcomes: ReviewOutcomeMetrics

    # Financial exposure
    financial: FinancialMetrics

    # Risk prioritization
    priority: PriorityMetrics

    # High-level operational indicators
    total_cases: int = Field(ge=0)
    high_risk_cases: int = Field(ge=0)
    critical_cases: int = Field(ge=0)
    open_cases: int = Field(ge=0)
    pending_review_cases: int = Field(ge=0)
    resolved_cases: int = Field(ge=0)