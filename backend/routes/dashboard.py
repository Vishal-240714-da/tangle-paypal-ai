from fastapi import APIRouter
from sqlalchemy import select

from database.connection import SessionLocal
from database.models import (
    Case,
    RiskAssessment,
    Review,
)


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"],
)


@router.get("/summary")
def dashboard_summary():

    session = SessionLocal()

    try:

        # -----------------------------
        # CASES
        # -----------------------------

        cases = session.scalars(
            select(Case)
        ).all()

        total_cases = len(cases)

        # -----------------------------
        # RISK ASSESSMENTS
        # -----------------------------

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

        # -----------------------------
        # FINANCIAL METRICS
        # -----------------------------

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
            sum(coverage_values) / len(coverage_values)
            if coverage_values
            else 0
        )

        # -----------------------------
        # REVIEW / LIFECYCLE
        # -----------------------------

        reviews = session.scalars(
            select(Review)
        ).all()

        resolved_or_approved = sum(
            1
            for review in reviews
            if review.case_status in {
                "APPROVED",
                "RESOLVED",
            }
        )

        # -----------------------------
        # RESPONSE
        # -----------------------------

        return {
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

    finally:
        session.close()