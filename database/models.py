from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    ForeignKey,
)

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


# ============================================================
# INVOICES
# ============================================================

class Invoice(Base):
    __tablename__ = "invoices"

    invoice_id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )

    customer: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    invoice_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    due_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    amount: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    currency: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )


# ============================================================
# PAYMENTS
# ============================================================

class Payment(Base):
    __tablename__ = "payments"

    payment_id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )

    invoice_id: Mapped[str | None] = mapped_column(
        String(100),
        ForeignKey("invoices.invoice_id"),
        nullable=True,
    )

    payment_invoice_reference: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    customer: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    payment_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    amount: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    currency: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )

    gateway_reference: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    payment_fee: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )


# ============================================================
# BANK TRANSACTIONS
# ============================================================

class BankTransaction(Base):
    __tablename__ = "bank_transactions"

    bank_transaction_id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )

    deposit_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    amount: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    currency: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )


# ============================================================
# CASES
# ============================================================

class Case(Base):
    __tablename__ = "cases"

    case_id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )

    record_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    record_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    invoice_id: Mapped[str | None] = mapped_column(
        String(100),
        ForeignKey("invoices.invoice_id"),
        nullable=True,
    )

    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    suggested_action: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    next_action: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ----------------------------
    # Financial information
    # ----------------------------

    payment_amount: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    bank_amount: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    payment_fee: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    outstanding_amount: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    payment_coverage_percent: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    bank_payment_difference: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    invoice_payment_difference: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    financial_status: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    financial_impact: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    original_invoice_amount: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    # ----------------------------
    # Decision information
    # ----------------------------

    decision: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    decision_confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    # ----------------------------
    # Related invoice information
    # ----------------------------

    related_invoice_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    related_invoice_ids: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )


# ============================================================
# INVESTIGATIONS
# ============================================================

class Investigation(Base):
    __tablename__ = "investigations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    case_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("cases.case_id"),
        nullable=False,
    )

    hypothesis: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    investigation_confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    rationale: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    investigation_action: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    investigation_finding: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    likely_cause: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    recommended_action: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    reasoning_steps: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    evidence_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )


# ============================================================
# RISK ASSESSMENTS
# ============================================================

class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    case_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("cases.case_id"),
        nullable=False,
    )

    risk_level: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    priority_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    human_review_required: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    risk_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    financial_impact: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )


# ============================================================
# REVIEWS
# ============================================================

class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    case_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("cases.case_id"),
        nullable=False,
    )

    case_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    review_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    reviewer_decision: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    reviewer_comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    final_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )