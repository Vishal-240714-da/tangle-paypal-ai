from collections import Counter

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from database.connection import SessionLocal
from database.models import (
    BankTransaction,
    Case,
    Invoice,
    Payment,
    Review,
    RiskAssessment,
)
from backend.schemas.analytics import (
    AnalyticsSummaryResponse,
    FinancialMetrics,
    HumanReviewMetrics,
    PriorityMetrics,
    ReviewOutcomeMetrics,
)


router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"],
)


# ============================================================
# HELPERS
# ============================================================

def build_distribution(values):
    """
    Build a case-insensitive distribution from a list of values.
    """
    counter = Counter()

    for value in values:
        if value is None:
            continue

        key = str(value).strip().upper()

        if key:
            counter[key] += 1

    return dict(counter)


def empty_analytics_response():
    """
    Return a valid empty analytics response.
    """
    return AnalyticsSummaryResponse(
        risk_distribution={},
        exception_distribution={},
        lifecycle_distribution={},
        decision_distribution={},
        human_review=HumanReviewMetrics(
            required=0,
            not_required=0,
            rate=0,
        ),
        review_outcomes=ReviewOutcomeMetrics(
            approved=0,
            rejected=0,
            escalated=0,
            pending=0,
            completion_rate=0,
        ),
        financial=FinancialMetrics(
            outstanding_balance=0,
            average_payment_coverage=0,
            total_invoice_amount=0,
            total_payment_amount=0,
            total_bank_amount=0,
        ),
        priority=PriorityMetrics(
            average=0,
            maximum=0,
            minimum=0,
        ),
        total_cases=0,
        high_risk_cases=0,
        critical_cases=0,
        open_cases=0,
        pending_review_cases=0,
        resolved_cases=0,
    )


# ============================================================
# SUMMARY
# ============================================================

@router.get(
    "/summary",
    response_model=AnalyticsSummaryResponse,
)
def get_analytics_summary():
    """
    Return the complete TANGLE analytics summary.
    """

    with SessionLocal() as db:
        cases = db.scalars(
            select(Case)
        ).all()

        risks = db.scalars(
            select(RiskAssessment)
        ).all()

        invoices = db.scalars(
            select(Invoice)
        ).all()

        payments = db.scalars(
            select(Payment)
        ).all()

        bank_transactions = db.scalars(
            select(BankTransaction)
        ).all()

        reviews = db.scalars(
            select(Review)
        ).all()

    if not cases and not risks and not invoices:
        return empty_analytics_response()

    # ========================================================
    # RISK DISTRIBUTION
    # ========================================================

    risk_distribution = build_distribution(
        risk.risk_level
        for risk in risks
    )

    # ========================================================
    # EXCEPTION DISTRIBUTION
    # ========================================================

    exception_distribution = build_distribution(
        case.category
        for case in cases
    )

    # ========================================================
    # LIFECYCLE DISTRIBUTION
    # ========================================================

    lifecycle_distribution = build_distribution(
        case.status
        for case in cases
    )

    # ========================================================
    # DECISION DISTRIBUTION
    # ========================================================

    decision_distribution = build_distribution(
        case.decision
        for case in cases
    )

    # ========================================================
    # HUMAN REVIEW
    # ========================================================

    human_review_required = sum(
        1
        for risk in risks
        if bool(risk.human_review_required)
    )

    human_review_not_required = max(
        len(risks) - human_review_required,
        0,
    )

    human_review_rate = (
        (
            human_review_required
            / len(risks)
        )
        * 100
        if risks
        else 0
    )

    # ========================================================
    # REVIEW OUTCOMES
    # ========================================================

    approved_reviews = 0
    rejected_reviews = 0
    escalated_reviews = 0
    pending_reviews = 0

    for review in reviews:
        decision = (
            review.reviewer_decision
            or review.decision
            or ""
        )

        decision = str(
            decision
        ).strip().upper()

        if decision == "APPROVE":
            approved_reviews += 1

        elif decision == "REJECT":
            rejected_reviews += 1

        elif decision == "ESCALATE":
            escalated_reviews += 1

        else:
            pending_reviews += 1

    completed_reviews = (
        approved_reviews
        + rejected_reviews
        + escalated_reviews
    )

    review_completion_rate = (
        (
            completed_reviews
            / len(reviews)
        )
        * 100
        if reviews
        else 0
    )

    # ========================================================
    # FINANCIAL METRICS
    # ========================================================

    outstanding_balance = sum(
        float(case.outstanding_amount or 0)
        for case in cases
    )

    payment_coverages = [
        float(
            case.payment_coverage_percent
        )
        for case in cases
        if case.payment_coverage_percent
        is not None
    ]

    average_payment_coverage = (
        sum(payment_coverages)
        / len(payment_coverages)
        if payment_coverages
        else 0
    )

    total_invoice_amount = sum(
        float(invoice.amount or 0)
        for invoice in invoices
    )

    total_payment_amount = sum(
        float(payment.amount or 0)
        for payment in payments
    )

    total_bank_amount = sum(
        float(transaction.amount or 0)
        for transaction in bank_transactions
    )

    # ========================================================
    # PRIORITY
    # ========================================================

    priority_scores = [
        float(risk.priority_score)
        for risk in risks
        if risk.priority_score is not None
    ]

    average_priority = (
        sum(priority_scores)
        / len(priority_scores)
        if priority_scores
        else 0
    )

    maximum_priority = (
        max(priority_scores)
        if priority_scores
        else 0
    )

    minimum_priority = (
        min(priority_scores)
        if priority_scores
        else 0
    )

    # ========================================================
    # OPERATIONAL METRICS
    # ========================================================

    total_cases = len(cases)

    high_risk_cases = sum(
        1
        for risk in risks
        if str(
            risk.risk_level or ""
        ).upper()
        in {"HIGH", "CRITICAL"}
    )

    critical_cases = sum(
        1
        for risk in risks
        if str(
            risk.risk_level or ""
        ).upper()
        == "CRITICAL"
    )

    open_cases = sum(
        1
        for case in cases
        if str(
            case.status or ""
        ).upper()
        == "OPEN"
    )

    pending_review_cases = sum(
        1
        for case in cases
        if str(
            case.status or ""
        ).upper()
        == "PENDING_REVIEW"
    )

    resolved_cases = sum(
        1
        for case in cases
        if str(
            case.status or ""
        ).upper()
        == "RESOLVED"
    )

    # ========================================================
    # RESPONSE
    # ========================================================

    return AnalyticsSummaryResponse(
        risk_distribution=risk_distribution,
        exception_distribution=exception_distribution,
        lifecycle_distribution=lifecycle_distribution,
        decision_distribution=decision_distribution,
        human_review=HumanReviewMetrics(
            required=human_review_required,
            not_required=human_review_not_required,
            rate=round(
                human_review_rate,
                2,
            ),
        ),
        review_outcomes=ReviewOutcomeMetrics(
            approved=approved_reviews,
            rejected=rejected_reviews,
            escalated=escalated_reviews,
            pending=pending_reviews,
            completion_rate=round(
                review_completion_rate,
                2,
            ),
        ),
        financial=FinancialMetrics(
            outstanding_balance=round(
                outstanding_balance,
                2,
            ),
            average_payment_coverage=round(
                average_payment_coverage,
                2,
            ),
            total_invoice_amount=round(
                total_invoice_amount,
                2,
            ),
            total_payment_amount=round(
                total_payment_amount,
                2,
            ),
            total_bank_amount=round(
                total_bank_amount,
                2,
            ),
        ),
        priority=PriorityMetrics(
            average=round(
                average_priority,
                2,
            ),
            maximum=round(
                maximum_priority,
                2,
            ),
            minimum=round(
                minimum_priority,
                2,
            ),
        ),
        total_cases=total_cases,
        high_risk_cases=high_risk_cases,
        critical_cases=critical_cases,
        open_cases=open_cases,
        pending_review_cases=pending_review_cases,
        resolved_cases=resolved_cases,
    )


# ============================================================
# RISK
# ============================================================

@router.get("/risk")
def get_risk_distribution():
    """
    Return case risk distribution.
    """

    with SessionLocal() as db:
        risks = db.scalars(
            select(RiskAssessment)
        ).all()

    return build_distribution(
        risk.risk_level
        for risk in risks
    )


# ============================================================
# EXCEPTIONS
# ============================================================

@router.get("/exceptions")
def get_exception_distribution():
    """
    Return exception category distribution.
    """

    with SessionLocal() as db:
        cases = db.scalars(
            select(Case)
        ).all()

    return build_distribution(
        case.category
        for case in cases
    )


# ============================================================
# LIFECYCLE
# ============================================================

@router.get("/lifecycle")
def get_lifecycle_distribution():
    """
    Return authoritative case lifecycle distribution.
    """

    with SessionLocal() as db:
        cases = db.scalars(
            select(Case)
        ).all()

    return build_distribution(
        case.status
        for case in cases
    )