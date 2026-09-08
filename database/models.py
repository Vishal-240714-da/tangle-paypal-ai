from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


# ============================================================
# USERS
# ============================================================

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="ANALYST",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )


# ============================================================
# INVOICES
# ============================================================

class Invoice(Base):
    __tablename__ = "invoices"

    invoice_id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )

    customer: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    invoice_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    due_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
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

    payment_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    gateway_reference: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    payment_fee: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
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

    payment_id: Mapped[str | None] = mapped_column(
        String(100),
        ForeignKey("payments.payment_id"),
        nullable=True,
    )

    deposit_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
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

    # --------------------------------------------------------
    # Existing TANGLE fields
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Financial information
    # --------------------------------------------------------

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

    # IMPORTANT:
    # PostgreSQL currently stores this field as VARCHAR.
    financial_impact: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    original_invoice_amount: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    # --------------------------------------------------------
    # Existing decision information
    # --------------------------------------------------------

    decision: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    decision_confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    related_invoice_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    related_invoice_ids: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # --------------------------------------------------------
    # Phase 2 - authoritative lifecycle
    # --------------------------------------------------------

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="OPEN",
    )

    risk_level: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    priority_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    human_review_required: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
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

    # --------------------------------------------------------
    # Existing fields
    # --------------------------------------------------------

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
        String(100),
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

    # --------------------------------------------------------
    # Phase 2 semantic fields
    # --------------------------------------------------------

    finding: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    recommendation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    evidence: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
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

    risk_score: Mapped[float | None] = mapped_column(
        Float,
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

    # Existing database column is VARCHAR.
    financial_impact: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
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

    # --------------------------------------------------------
    # Existing fields
    # --------------------------------------------------------

    case_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    review_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    reviewer_decision: Mapped[str | None] = mapped_column(
        String(100),
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

    # --------------------------------------------------------
    # Phase 2 semantic fields
    # --------------------------------------------------------

    reviewer: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    decision: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )


# ============================================================
# CASE HISTORY / AUDIT TRAIL
# ============================================================

class CaseHistory(Base):
    __tablename__ = "case_history"

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

    previous_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    new_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    changed_by: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )