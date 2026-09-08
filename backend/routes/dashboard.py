import logging

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from backend.schemas.dashboard import DashboardSummaryResponse
from database.connection import SessionLocal
from database.models import Case, RiskAssessment


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"],
)


# ============================================================
# DASHBOARD SUMMARY
# ============================================================

@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    summary="Get dashboard summary",
    description=(
        "Return the main TANGLE dashboard metrics "
        "including case counts, risk, human review and "
        "financial metrics."
    ),
)
def dashboard_summary():
    """
    Return the main TANGLE dashboard metrics.

    Case.status is the authoritative source for
    lifecycle-related dashboard metrics.
    """

    session = SessionLocal()

    try:
        # ----------------------------------------------------
        # CASES
        # ----------------------------------------------------

        cases = session.scalars(
            select(Case)
        ).all()

        total_cases = len(cases)

        # ----------------------------------------------------
        # RISK ASSESSMENTS
        # ----------------------------------------------------

        risk_assessments = session.scalars(
            select(RiskAssessment)
        ).all()

        critical_cases = sum(
            1
            for risk in risk_assessments
            if risk.risk_level == "CRITICAL"
        )

        high_risk_cases = sum(
            1
            for risk in risk_assessments
            if risk.risk_level == "HIGH"
        )

        human_review = sum(
            1
            for risk in risk_assessments
            if risk.human_review_required is True
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

        # ----------------------------------------------------
        # LIFECYCLE
        #
        # IMPORTANT:
        # Case.status is the authoritative lifecycle source.
        # ----------------------------------------------------

        resolved_or_approved = sum(
            1
            for case in cases
            if case.status in {
                "APPROVED",
                "RESOLVED",
            }
        )

        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        result = {
            "total_cases": total_cases,
            "critical_cases": critical_cases,
            "high_risk_cases": high_risk_cases,
            "human_review": human_review,
            "outstanding_balance": round(
                outstanding_balance,
                2,
            ),
            "average_payment_coverage": round(
                average_payment_coverage,
                2,
            ),
            "resolved_or_approved": resolved_or_approved,
        }

        logger.info(
            "Dashboard summary generated: "
            "total_cases=%s resolved_or_approved=%s",
            total_cases,
            resolved_or_approved,
        )

        return result

    except Exception:
        session.rollback()

        logger.exception(
            "Failed to generate dashboard summary."
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to generate dashboard summary.",
        )

    finally:
        session.close()