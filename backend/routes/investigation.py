import logging

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from database.connection import SessionLocal
from database.models import (
    Case,
    Investigation,
    RiskAssessment,
    Review,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/investigation",
    tags=["Investigation"],
)


def safe_float(value):
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def build_evidence(case):
    """
    Build explainable evidence directly from the
    financial values stored for the case.
    """

    evidence = []

    currency = getattr(case, "currency", None) or "INR"

    invoice_amount = safe_float(
        getattr(
            case,
            "original_invoice_amount",
            None,
        )
    )

    payment_amount = safe_float(
        getattr(
            case,
            "payment_amount",
            None,
        )
    )

    bank_amount = safe_float(
        getattr(
            case,
            "bank_amount",
            None,
        )
    )

    payment_fee = safe_float(
        getattr(
            case,
            "payment_fee",
            None,
        )
    )

    outstanding_amount = safe_float(
        getattr(
            case,
            "outstanding_amount",
            None,
        )
    )

    coverage = safe_float(
        getattr(
            case,
            "payment_coverage_percent",
            None,
        )
    )

    invoice_payment_difference = safe_float(
        getattr(
            case,
            "invoice_payment_difference",
            None,
        )
    )

    bank_payment_difference = safe_float(
        getattr(
            case,
            "bank_payment_difference",
            None,
        )
    )

    if invoice_amount is not None:
        evidence.append(
            {
                "label": "Invoice Amount",
                "value": (
                    f"{currency} "
                    f"{invoice_amount:,.2f}"
                ),
                "source": "Invoice",
            }
        )

    if payment_amount is not None:
        evidence.append(
            {
                "label": "Payment Amount",
                "value": (
                    f"{currency} "
                    f"{payment_amount:,.2f}"
                ),
                "source": "Payment",
            }
        )

    if bank_amount is not None:
        evidence.append(
            {
                "label": "Bank Amount",
                "value": (
                    f"{currency} "
                    f"{bank_amount:,.2f}"
                ),
                "source": "Bank Transaction",
            }
        )

    if invoice_amount is not None and payment_amount is not None:
        if outstanding_amount is None:
            outstanding_amount = max(
                invoice_amount - payment_amount,
                0,
            )

        evidence.append(
            {
                "label": "Outstanding Amount",
                "value": (
                    f"{currency} "
                    f"{outstanding_amount:,.2f}"
                ),
                "source": "Calculated",
            }
        )

        if coverage is None and invoice_amount != 0:
            coverage = (
                payment_amount
                / invoice_amount
                * 100
            )

        evidence.append(
            {
                "label": "Payment Coverage",
                "value": (
                    f"{coverage:.2f}%"
                    if coverage is not None
                    else "N/A"
                ),
                "source": "Calculated",
            }
        )

        evidence.append(
            {
                "label": "Invoice-Payment Difference",
                "value": (
                    f"{currency} "
                    f"{invoice_payment_difference:,.2f}"
                    if invoice_payment_difference is not None
                    else (
                        f"{currency} "
                        f"{invoice_amount - payment_amount:,.2f}"
                    )
                ),
                "source": "Calculated",
            }
        )

    if (
        payment_amount is not None
        and bank_amount is not None
    ):
        if bank_payment_difference is None:
            bank_payment_difference = (
                bank_amount - payment_amount
            )

        evidence.append(
            {
                "label": "Bank-Payment Difference",
                "value": (
                    f"{currency} "
                    f"{bank_payment_difference:,.2f}"
                ),
                "source": "Calculated",
            }
        )

    if payment_fee is not None and payment_fee != 0:
        evidence.append(
            {
                "label": "Payment Fee",
                "value": (
                    f"{currency} "
                    f"{payment_fee:,.2f}"
                ),
                "source": "Payment",
            }
        )

    return evidence


def get_review_data(review, case):
    if review is None:
        return {
            "case_status": getattr(
                case,
                "status",
                None,
            ),
            "review_status": "PENDING",
            "reviewer": None,
            "reviewer_decision": None,
            "comment": None,
            "final_status": getattr(
                case,
                "status",
                None,
            ),
        }

    decision = getattr(
        review,
        "decision",
        None,
    )

    return {
        "case_status": getattr(
            case,
            "status",
            None,
        ),
        "review_status": (
            "COMPLETED"
            if decision
            else "PENDING"
        ),
        "reviewer": getattr(
            review,
            "reviewer",
            None,
        ),
        "reviewer_decision": decision,
        "comment": getattr(
            review,
            "comment",
            None,
        ),
        "final_status": getattr(
            case,
            "status",
            None,
        ),
    }


@router.get(
    "/{case_id}",
    summary="Get explainable investigation by case ID",
)
def get_investigation(case_id: str):
    case_id = case_id.strip()

    if not case_id:
        raise HTTPException(
            status_code=400,
            detail="Case ID cannot be empty.",
        )

    session = SessionLocal()

    try:
        # ----------------------------------------------------
        # CASE
        # ----------------------------------------------------

        case = session.scalars(
            select(Case).where(
                Case.case_id == case_id
            )
        ).first()

        if case is None:
            raise HTTPException(
                status_code=404,
                detail=f"Case {case_id} not found.",
            )

        # ----------------------------------------------------
        # INVESTIGATION
        # ----------------------------------------------------

        investigation = session.scalars(
            select(Investigation)
            .where(
                Investigation.case_id == case_id
            )
        ).first()

        if investigation is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Investigation for case "
                    f"{case_id} not found."
                ),
            )

        # ----------------------------------------------------
        # RISK
        # ----------------------------------------------------

        risk = session.scalars(
            select(RiskAssessment)
            .where(
                RiskAssessment.case_id == case_id
            )
            .order_by(
                RiskAssessment.created_at.desc()
            )
        ).first()

        # ----------------------------------------------------
        # REVIEW
        # ----------------------------------------------------

        review = session.scalars(
            select(Review)
            .where(
                Review.case_id == case_id
            )
            .order_by(
                Review.created_at.desc()
            )
        ).first()

        # ----------------------------------------------------
        # FINANCIAL DATA
        # ----------------------------------------------------

        invoice_amount = safe_float(
            getattr(
                case,
                "original_invoice_amount",
                None,
            )
        )

        payment_amount = safe_float(
            getattr(
                case,
                "payment_amount",
                None,
            )
        )

        bank_amount = safe_float(
            getattr(
                case,
                "bank_amount",
                None,
            )
        )

        payment_fee = safe_float(
            getattr(
                case,
                "payment_fee",
                None,
            )
        ) or 0.0

        outstanding_amount = safe_float(
            getattr(
                case,
                "outstanding_amount",
                None,
            )
        )

        coverage = safe_float(
            getattr(
                case,
                "payment_coverage_percent",
                None,
            )
        )

        invoice_payment_difference = safe_float(
            getattr(
                case,
                "invoice_payment_difference",
                None,
            )
        )

        bank_payment_difference = safe_float(
            getattr(
                case,
                "bank_payment_difference",
                None,
            )
        )

        # ----------------------------------------------------
        # FALLBACK CALCULATIONS
        # ----------------------------------------------------

        if (
            outstanding_amount is None
            and invoice_amount is not None
            and payment_amount is not None
        ):
            outstanding_amount = max(
                invoice_amount - payment_amount,
                0,
            )

        if (
            coverage is None
            and invoice_amount
            and payment_amount is not None
        ):
            coverage = (
                payment_amount
                / invoice_amount
                * 100
            )

        if (
            invoice_payment_difference is None
            and invoice_amount is not None
            and payment_amount is not None
        ):
            invoice_payment_difference = (
                invoice_amount - payment_amount
            )

        if (
            bank_payment_difference is None
            and bank_amount is not None
            and payment_amount is not None
        ):
            bank_payment_difference = (
                bank_amount - payment_amount
            )

        # ----------------------------------------------------
        # CURRENCY
        # ----------------------------------------------------

        currency = (
            getattr(
                case,
                "currency",
                None,
            )
            or "INR"
        )

        # ----------------------------------------------------
        # EXPLAINABLE EVIDENCE
        # ----------------------------------------------------

        evidence = build_evidence(case)

        # ----------------------------------------------------
        # FINANCIAL RESPONSE
        # ----------------------------------------------------

        financial = {
            "invoice_amount": invoice_amount,
            "payment_amount": payment_amount,
            "bank_amount": bank_amount,
            "payment_fee": payment_fee,
            "outstanding_amount": outstanding_amount,
            "payment_coverage_percent": coverage,
            "invoice_payment_difference":
                invoice_payment_difference,
            "bank_payment_difference":
                bank_payment_difference,
            "financial_status":
                getattr(
                    case,
                    "financial_status",
                    None,
                ),
            "financial_impact":
                getattr(
                    case,
                    "financial_impact",
                    None,
                ),
            "currency": currency,
        }

        # ----------------------------------------------------
        # AI INVESTIGATION
        # ----------------------------------------------------

        confidence = (
            investigation.investigation_confidence
            if investigation.investigation_confidence
            is not None
            else investigation.confidence
        )

        ai_investigation = {
            "finding": (
                investigation.investigation_finding
                or investigation.finding
                or investigation.hypothesis
            ),
            "likely_cause":
                investigation.likely_cause,
            "recommendation": (
                investigation.recommended_action
                or investigation.recommendation
            ),
            "confidence": confidence,
            "evidence": evidence,
            "reasoning":
                investigation.reasoning_steps,
            "rationale":
                investigation.rationale,
            "evidence_summary":
                investigation.evidence_summary,
        }

        # ----------------------------------------------------
        # CASE RESPONSE
        # ----------------------------------------------------

        case_response = {
            "case_id":
                case.case_id,

            "status":
                getattr(
                    case,
                    "status",
                    None,
                ),

            "record_type":
                getattr(
                    case,
                    "record_type",
                    None,
                ),

            "record_id":
                getattr(
                    case,
                    "record_id",
                    None,
                ),

            "invoice_id":
                getattr(
                    case,
                    "invoice_id",
                    None,
                ),

            "category":
                getattr(
                    case,
                    "category",
                    None,
                ),

            "exception_type":
                getattr(
                    case,
                    "exception_type",
                    None,
                ),

            "payment_id":
                getattr(
                    case,
                    "payment_id",
                    None,
                ),

            "decision":
                getattr(
                    case,
                    "decision",
                    None,
                ),

            "decision_confidence":
                getattr(
                    case,
                    "decision_confidence",
                    None,
                ),

            "confidence":
                getattr(
                    case,
                    "confidence",
                    None,
                ),

            "suggested_action":
                getattr(
                    case,
                    "suggested_action",
                    None,
                ),

            "related_invoice_count":
                getattr(
                    case,
                    "related_invoice_count",
                    None,
                ),

            "related_invoice_ids":
                getattr(
                    case,
                    "related_invoice_ids",
                    None,
                ),

            "human_review_required":
                getattr(
                    case,
                    "human_review_required",
                    None,
                ),
        }

        # ----------------------------------------------------
        # RISK RESPONSE
        # ----------------------------------------------------

        risk_response = {
            "risk_level":
                getattr(
                    risk,
                    "risk_level",
                    None,
                ) if risk else getattr(
                    case,
                    "risk_level",
                    None,
                ),

            "risk_score":
                getattr(
                    risk,
                    "risk_score",
                    None,
                ) if risk else None,

            "priority_score":
                getattr(
                    case,
                    "priority_score",
                    None,
                ),

            "human_review_required":
                getattr(
                    case,
                    "human_review_required",
                    None,
                ),

            "risk_reason":
                getattr(
                    risk,
                    "risk_reason",
                    None,
                ) if risk else None,
        }

        logger.info(
            "Explainable investigation retrieved: %s",
            case_id,
        )

        return {
            "case": case_response,
            "financial": financial,
            "ai_investigation":
                ai_investigation,
            "risk": risk_response,
            "review":
                get_review_data(
                    review,
                    case,
                ),
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            "Failed to retrieve investigation for %s",
            case_id,
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve investigation.",
        )

    finally:
        session.close()