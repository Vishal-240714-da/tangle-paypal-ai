import logging

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from database.connection import SessionLocal
from database.models import (
    Invoice,
    Payment,
    BankTransaction,
    Case,
    RiskAssessment,
)

from backend.schemas.analytics import (
    AnalyticsSummaryResponse,
    HumanReviewMetrics,
    FinancialMetrics,
    PriorityMetrics,
)


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"],
)


# ============================================================
# HELPERS
# ============================================================

def build_distribution(values):
    """
    Build a clean uppercase distribution dictionary.
    """

    distribution = {}

    for value in values:
        key = (
            str(value).strip().upper()
            if value is not None
            else "UNKNOWN"
        )

        if not key:
            key = "UNKNOWN"

        distribution[key] = (
            distribution.get(key, 0) + 1
        )

    return distribution


def empty_analytics_response():
    """
    Return a valid empty analytics response.
    """

    return {
        "risk_distribution": {},
        "exception_distribution": {},
        "lifecycle_distribution": {},
        "decision_distribution": {},
        "human_review": {
            "required": 0,
            "not_required": 0,
            "rate": 0,
        },
        "financial": {
            "outstanding_balance": 0,
            "average_payment_coverage": 0,
            "total_invoice_amount": 0,
            "total_payment_amount": 0,
            "total_bank_amount": 0,
        },
        "priority": {
            "average": 0,
            "maximum": 0,
            "minimum": 0,
        },
    }


# ============================================================
# ANALYTICS SUMMARY
# ============================================================

@router.get(
    "/summary",
    response_model=AnalyticsSummaryResponse,
    summary="Get analytics summary",
    description=(
        "Return aggregate TANGLE analytics including "
        "risk, exceptions, lifecycle, decisions, "
        "human review, financial metrics and priority."
    ),
)
def analytics_summary():
    """
    Return complete analytics data from PostgreSQL.
    """

    session = SessionLocal()

    try:
        # ----------------------------------------------------
        # LOAD DATA
        # ----------------------------------------------------

        cases = session.scalars(
            select(Case)
        ).all()

        risk_assessments = session.scalars(
            select(RiskAssessment)
        ).all()

        invoices = session.scalars(
            select(Invoice)
        ).all()

        payments = session.scalars(
            select(Payment)
        ).all()

        bank_transactions = session.scalars(
            select(BankTransaction)
        ).all()

        # ----------------------------------------------------
        # EMPTY DATABASE
        # ----------------------------------------------------

        if not cases:
            logger.info(
                "Analytics requested for empty database."
            )

            return empty_analytics_response()

        # ----------------------------------------------------
        # RISK DISTRIBUTION
        # ----------------------------------------------------

        risk_distribution = build_distribution(
            risk.risk_level
            for risk in risk_assessments
        )

        # ----------------------------------------------------
        # EXCEPTION DISTRIBUTION
        # ----------------------------------------------------

        exception_distribution = build_distribution(
            case.category
            for case in cases
        )

        # ----------------------------------------------------
        # LIFECYCLE DISTRIBUTION
        #
        # IMPORTANT:
        # Case.status is the authoritative lifecycle state.
        # ----------------------------------------------------

        lifecycle_distribution = build_distribution(
            case.status
            for case in cases
        )

        # ----------------------------------------------------
        # AI DECISION DISTRIBUTION
        # ----------------------------------------------------

        decision_distribution = build_distribution(
            case.decision
            for case in cases
        )

        # ----------------------------------------------------
        # HUMAN REVIEW
        # ----------------------------------------------------

        required = sum(
            1
            for risk in risk_assessments
            if risk.human_review_required is True
        )

        not_required = max(
            len(cases) - required,
            0,
        )

        review_rate = (
            (required / len(cases)) * 100
            if cases
            else 0
        )

        # ----------------------------------------------------
        # FINANCIAL METRICS
        # ----------------------------------------------------

        outstanding_balance = sum(
            case.outstanding_amount or 0
            for case in cases
        )

        coverage_values = [
            case.payment_coverage_percent
            for case in cases
            if case.payment_coverage_percent is not None
        ]

        average_payment_coverage = (
            sum(coverage_values)
            / len(coverage_values)
            if coverage_values
            else 0
        )

        total_invoice_amount = sum(
            invoice.amount or 0
            for invoice in invoices
        )

        total_payment_amount = sum(
            payment.amount or 0
            for payment in payments
        )

        total_bank_amount = sum(
            transaction.amount or 0
            for transaction in bank_transactions
        )

        # ----------------------------------------------------
        # PRIORITY
        # ----------------------------------------------------

        priority_values = [
            risk.priority_score
            for risk in risk_assessments
            if risk.priority_score is not None
        ]

        average_priority = (
            sum(priority_values)
            / len(priority_values)
            if priority_values
            else 0
        )

        maximum_priority = (
            max(priority_values)
            if priority_values
            else 0
        )

        minimum_priority = (
            min(priority_values)
            if priority_values
            else 0
        )

        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        result = {
            "risk_distribution": risk_distribution,

            "exception_distribution": (
                exception_distribution
            ),

            "lifecycle_distribution": (
                lifecycle_distribution
            ),

            "decision_distribution": (
                decision_distribution
            ),

            "human_review": {
                "required": required,
                "not_required": not_required,
                "rate": round(
                    review_rate,
                    2,
                ),
            },

            "financial": {
                "outstanding_balance": round(
                    outstanding_balance,
                    2,
                ),

                "average_payment_coverage": round(
                    average_payment_coverage,
                    2,
                ),

                "total_invoice_amount": round(
                    total_invoice_amount,
                    2,
                ),

                "total_payment_amount": round(
                    total_payment_amount,
                    2,
                ),

                "total_bank_amount": round(
                    total_bank_amount,
                    2,
                ),
            },

            "priority": {
                "average": round(
                    average_priority,
                    2,
                ),

                "maximum": round(
                    maximum_priority,
                    2,
                ),

                "minimum": round(
                    minimum_priority,
                    2,
                ),
            },
        }

        logger.info(
            "Analytics summary generated successfully."
        )

        return result

    except Exception:
        session.rollback()

        logger.exception(
            "Failed to generate analytics summary."
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to generate analytics summary.",
        )

    finally:
        session.close()


# ============================================================
# RISK
# ============================================================

@router.get(
    "/risk",
    response_model=dict[str, int],
    summary="Get risk distribution",
)
def risk_distribution():
    """
    Return only the risk distribution.
    """

    session = SessionLocal()

    try:
        risk_assessments = session.scalars(
            select(RiskAssessment)
        ).all()

        result = build_distribution(
            risk.risk_level
            for risk in risk_assessments
        )

        logger.info(
            "Risk analytics generated."
        )

        return result

    except Exception:
        session.rollback()

        logger.exception(
            "Failed to generate risk analytics."
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to generate risk analytics.",
        )

    finally:
        session.close()


# ============================================================
# EXCEPTIONS
# ============================================================

@router.get(
    "/exceptions",
    response_model=dict[str, int],
    summary="Get exception distribution",
)
def exception_distribution():
    """
    Return exception category distribution.
    """

    session = SessionLocal()

    try:
        cases = session.scalars(
            select(Case)
        ).all()

        result = build_distribution(
            case.category
            for case in cases
        )

        logger.info(
            "Exception analytics generated."
        )

        return result

    except Exception:
        session.rollback()

        logger.exception(
            "Failed to generate exception analytics."
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to generate exception analytics.",
        )

    finally:
        session.close()


# ============================================================
# LIFECYCLE
# ============================================================

@router.get(
    "/lifecycle",
    response_model=dict[str, int],
    summary="Get lifecycle distribution",
    description=(
        "Return the current TANGLE case lifecycle "
        "distribution using Case.status."
    ),
)
def lifecycle_distribution():
    """
    Return the current case lifecycle distribution.

    Case.status is the authoritative lifecycle source.
    """

    session = SessionLocal()

    try:
        cases = session.scalars(
            select(Case)
        ).all()

        result = build_distribution(
            case.status
            for case in cases
        )

        logger.info(
            "Lifecycle analytics generated."
        )

        return result

    except Exception:
        session.rollback()

        logger.exception(
            "Failed to generate lifecycle analytics."
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to generate lifecycle analytics.",
        )

    finally:
        session.close()