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


class AnalyticsSummaryResponse(BaseModel):
    risk_distribution: dict[str, int]
    exception_distribution: dict[str, int]
    lifecycle_distribution: dict[str, int]
    decision_distribution: dict[str, int]
    human_review: HumanReviewMetrics
    financial: FinancialMetrics
    priority: PriorityMetrics