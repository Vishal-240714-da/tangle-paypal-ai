from pydantic import BaseModel


class DashboardSummaryResponse(BaseModel):
    total_cases: int
    critical_cases: int
    high_risk_cases: int
    human_review: int
    outstanding_balance: float
    average_payment_coverage: float
    resolved_or_approved: int