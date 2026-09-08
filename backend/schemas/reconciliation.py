from pydantic import BaseModel, Field


class ReconciliationItem(BaseModel):
    invoice_id: str | None = None
    payment_id: str | None = None
    bank_transaction_id: str | None = None

    pass_status: int = Field(ge=1)
    match_type: str
    confidence: float = Field(ge=0, le=1)
    rationale: str

    invoice_amount: float | None = None
    invoice_currency: str | None = None
    invoice_date: str | None = None

    payment_amount: float | None = None
    payment_currency: str | None = None
    payment_date: str | None = None

    bank_amount: float | None = None
    bank_currency: str | None = None
    bank_date: str | None = None

    payment_invoice_difference: float | None = None
    bank_payment_difference: float | None = None
    payment_coverage_percent: float | None = None


class ReconciliationSummary(BaseModel):
    total: int = Field(ge=0)
    exact: int = Field(ge=0)
    fuzzy: int = Field(ge=0)
    merged_payment: int = Field(ge=0)
    failed: int = Field(ge=0)
    average_confidence: float = Field(ge=0, le=1)


class ReconciliationResponse(BaseModel):
    items: list[ReconciliationItem]
    total: int = Field(ge=0)
    summary: ReconciliationSummary