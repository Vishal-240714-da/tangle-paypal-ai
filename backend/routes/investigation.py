import json
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


# ============================================================
# HELPERS
# ============================================================

def safe_float(value):
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def clean_explainable_text(value):
    """
    Normalize explainability text before returning it through the API.

    Repairs malformed word concatenations found in older
    investigation records.
    """
    if value is None:
        return None

    import re

    text = str(value)

    replacements = [
        # Common investigation phrases
        (r"Thepayment", "The payment"),
        (r"PaymentPAY-", "Payment PAY-"),
        (r"paymentrecord", "payment record"),
        (r"paymentrecords", "payment records"),
        (r"invoicerecord", "invoice record"),
        (r"invoicerecords", "invoice records"),
        (r"recordexists", "record exists"),

        # Bank / statement phrases
        (r"banktransaction", "bank transaction"),
        (r"banktransactions", "bank transactions"),
        (r"bankrecord", "bank record"),
        (r"bankrecords", "bank records"),
        (r"bankstatement", "bank statement"),
        (r"bankstatements", "bank statements"),
        (r"statemententry", "statement entry"),
        (r"statemententries", "statement entries"),
        (r"postinghistory", "posting history"),

        # Payment / verification phrases
        (r"paymenttherefore", "payment therefore"),
        (r"thereforecannot", "therefore cannot"),
        (r"paymentcannot", "payment cannot"),
        (r"cannotbe", "cannot be"),
        (r"cannotfully", "cannot fully"),
        (r"cannotconfirm", "cannot confirm"),
        (r"couldnotbe", "could not be"),
        (r"couldnot", "could not"),
        (r"wasnot", "was not"),
        (r"werenot", "were not"),
        (r"hasnot", "has not"),
        (r"hasbeen", "has been"),
        (r"notfound", "not found"),
        (r"notmatched", "not matched"),
        (r"notverified", "not verified"),
        (r"notlocated", "not located"),
        (r"notidentified", "not identified"),
        (r"notavailable", "not available"),

        # Modal / status phrases
        (r"couldbe", "could be"),
        (r"shouldbe", "should be"),
        (r"wouldbe", "would be"),
        (r"mayhave", "may have"),
        (r"maynot", "may not"),
        (r"wasfound", "was found"),
        (r"wasidentified", "was identified"),
        (r"wereidentified", "were identified"),
        (r"isavailable", "is available"),
        (r"isfound", "is found"),
        (r"ismissing", "is missing"),
        (r"isnot", "is not"),
        (r"aremissing", "are missing"),
        (r"areavailable", "are available"),

        # Action phrases
        (r"shouldbechecked", "should be checked"),
        (r"needstobe", "needs to be"),
        (r"needstocheck", "needs to check"),
        (r"checkthe", "check the"),
        (r"verifythe", "verify the"),
        (r"searchthe", "search the"),
        (r"reviewthe", "review the"),
        (r"confirmthe", "confirm the"),
        (r"comparethe", "compare the"),
        (r"matchthe", "match the"),

        # Connector phrases
        (r"againstthe", "against the"),
        (r"withthe", "with the"),
        (r"fromthe", "from the"),
        (r"inthe", "in the"),
        (r"onthe", "on the"),
        (r"tothe", "to the"),
        (r"ofthe", "of the"),
        (r"forthe", "for the"),

        # Investigation wording
        (r"determinewhether", "determine whether"),
        (r"delayedor", "delayed or"),
        (r"historyshould", "history should"),
        (r"historyand", "history and"),
        (r"amountcontains", "amount contains"),

        # Financial wording
        (r"financialrecords", "financial records"),
        (r"financialstatus", "financial status"),
        (r"financialimpact", "financial impact"),
        (r"invoiceamount", "invoice amount"),
        (r"paymentamount", "payment amount"),
        (r"bankamount", "bank amount"),
        (r"outstandingamount", "outstanding amount"),
        (r"paymentfee", "payment fee"),

        # Other TANGLE terminology
        (r"paymentgateway", "payment gateway"),
        (r"paymentdata", "payment data"),
        (r"paymentstatus", "payment status"),
        (r"risklevel", "risk level"),
        (r"priorityscore", "priority score"),
        (r"humanreviewrequired", "human review required"),
        (r"humanreview", "human review"),

        # Sentence spacing
        (r"located\.The", "located. The"),
        (r"records\.The", "records. The"),
        (r"\.The", ". The"),
        (r"\.This", ". This"),

        # Comma spacing
        (r",but", ", but"),
        (r",and", ", and"),
        (r",or", ", or"),
        (r",which", ", which"),
        (r",because", ", because"),
        (r",then", ", then"),

        # Financial summary spacing
        (r"amount:2500\.00", "amount: 2500.00"),
        (r"amount:\s*2500\.00\|", "amount: 2500.00 |"),
        (r"Payment amount:\s*2500\.00\|", "Payment amount: 2500.00 |"),
        (r"Outstanding amount:\s*0\.00\|", "Outstanding amount: 0.00 |"),

        # Generic pipe spacing
        (r"\s*\|\s*", " | "),
    ]

    for pattern, replacement in replacements:
        text = re.sub(
            pattern,
            replacement,
            text,
        )

    # Collapse accidental repeated whitespace.
    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    ).strip()

    return text

def clean_reasoning(value):
    """
    Convert stored JSON-encoded reasoning into a real list.

    Older records may contain reasoning_steps as a JSON string
    containing a list. Newer records may already contain a list.

    If parsing fails, preserve the complete value as a single
    reasoning step rather than returning malformed JSON text.
    """
    if value is None:
        return []

    if isinstance(value, list):
        return [
            clean_explainable_text(str(step))
            for step in value
        ]

    text = str(value).strip()

    if not text:
        return []

    try:
        parsed = json.loads(text)

        if isinstance(parsed, list):
            return [
                clean_explainable_text(str(step))
                for step in parsed
            ]

    except (json.JSONDecodeError, TypeError, ValueError):
        pass

    return [
        clean_explainable_text(text)
    ]


# ============================================================
# EVIDENCE BUILDER
# ============================================================

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

    # --------------------------------------------------------
    # INVOICE
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # PAYMENT
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # BANK
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # CALCULATED FINANCIAL VALUES
    # --------------------------------------------------------

    if (
        invoice_amount is not None
        and payment_amount is not None
    ):
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

    # --------------------------------------------------------
    # BANK-PAYMENT DIFFERENCE
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # PAYMENT FEE
    # --------------------------------------------------------

    if (
        payment_fee is not None
        and payment_fee != 0
    ):
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


# ============================================================
# REVIEW DATA
# ============================================================

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


# ============================================================
# INVESTIGATION ENDPOINT
# ============================================================

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

        finding = (
            investigation.investigation_finding
            or investigation.finding
            or investigation.hypothesis
        )

        likely_cause = investigation.likely_cause

        recommendation = (
            investigation.recommended_action
            or investigation.recommendation
        )

        rationale = investigation.rationale

        evidence_summary = investigation.evidence_summary

        reasoning = clean_reasoning(
            investigation.reasoning_steps
        )

        ai_investigation = {
            "finding": clean_explainable_text(
                finding
            ),
            "likely_cause": clean_explainable_text(
                likely_cause
            ),
            "recommendation": clean_explainable_text(
                recommendation
            ),
            "confidence": confidence,
            "evidence": evidence,
            "reasoning": reasoning,
            "rationale": clean_explainable_text(
                rationale
            ),
            "evidence_summary": clean_explainable_text(
                evidence_summary
            ),
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
                (
                    getattr(
                        risk,
                        "risk_level",
                        None,
                    )
                    if risk
                    else getattr(
                        case,
                        "risk_level",
                        None,
                    )
                ),

            "risk_score":
                (
                    getattr(
                        risk,
                        "risk_score",
                        None,
                    )
                    if risk
                    else None
                ),

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
                (
                    getattr(
                        risk,
                        "risk_reason",
                        None,
                    )
                    if risk
                    else None
                ),
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