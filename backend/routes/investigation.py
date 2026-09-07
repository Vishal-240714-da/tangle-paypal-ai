from fastapi import APIRouter, HTTPException

from backend.services.data_service import (
    get_case,
    get_investigation,
    get_risk_assessment,
    get_review,
    get_invoice,
    get_payment,
    get_bank_transaction,
)


router = APIRouter(
    prefix="/api/investigation",
    tags=["Investigation"],
)


def clean_value(value):
    """
    Convert database values into JSON-safe Python values.
    """

    if value is None:
        return None

    return value


@router.get("/{case_id}")
def get_investigation_details(case_id: str):

    case_id = case_id.strip()

    # --------------------------------
    # CASE
    # --------------------------------

    case = get_case(case_id)

    if case is None:
        raise HTTPException(
            status_code=404,
            detail=f"Case {case_id} not found.",
        )

    # --------------------------------
    # INVESTIGATION
    # --------------------------------

    investigation = get_investigation(case_id)

    # --------------------------------
    # RISK
    # --------------------------------

    risk = get_risk_assessment(case_id)

    # --------------------------------
    # REVIEW
    # --------------------------------

    review = get_review(case_id)

    # --------------------------------
    # INVOICE
    # --------------------------------

    invoice = None

    if case.invoice_id:
        invoice = get_invoice(case.invoice_id)

    # --------------------------------
    # PAYMENT / BANK TRANSACTION
    # --------------------------------

    payment = None
    bank_transaction = None

    if case.record_type:

        record_type = case.record_type.upper()

        if record_type == "PAYMENT":
            payment = get_payment(case.record_id)

        elif record_type in {
            "BANK",
            "BANK_TRANSACTION",
        }:
            bank_transaction = get_bank_transaction(
                case.record_id
            )

    # --------------------------------
    # TRANSACTION INFORMATION
    # --------------------------------

    payment_invoice_reference = None
    payment_customer = None
    payment_date = None
    payment_amount = case.payment_amount
    payment_currency = None
    gateway_reference = None
    payment_id = None

    if payment:

        payment_id = payment.payment_id
        payment_invoice_reference = (
            payment.payment_invoice_reference
        )
        payment_customer = payment.customer
        payment_date = payment.payment_date
        payment_amount = payment.amount
        payment_currency = payment.currency

        # gateway_reference is not currently
        # stored in the Payment model.
        gateway_reference = None

    bank_transaction_id = None
    bank_deposit_date = None
    bank_currency = None
    bank_amount = case.bank_amount

    if bank_transaction:

        bank_transaction_id = (
            bank_transaction.bank_transaction_id
        )
        bank_deposit_date = (
            bank_transaction.deposit_date
        )
        bank_currency = bank_transaction.currency
        bank_amount = bank_transaction.amount

    # --------------------------------
    # CASE STATUS
    # --------------------------------

    case_status = "OPEN"
    review_status = None
    final_status = None
    reviewer_decision = None
    reviewer_comment = None
    reviewed_at = None

    if review:

        case_status = review.case_status or "OPEN"
        review_status = review.review_status
        final_status = review.final_status
        reviewer_decision = review.reviewer_decision
        reviewer_comment = review.reviewer_comment
        reviewed_at = review.reviewed_at

    # --------------------------------
    # RESPONSE
    # --------------------------------

    result = {

        "case": {
            "case_id": case.case_id,
            "status": case_status,
            "review_status": review_status,
            "final_status": final_status,
            "decision": case.decision,
        },

        "transaction": {

            "record_type": case.record_type,
            "record_id": case.record_id,

            "invoice_id": case.invoice_id,

            "invoice_customer": (
                invoice.customer
                if invoice
                else None
            ),

            "invoice_date": (
                invoice.invoice_date
                if invoice
                else None
            ),

            "due_date": (
                invoice.due_date
                if invoice
                else None
            ),

            "invoice_amount": (
                invoice.amount
                if invoice
                else case.original_invoice_amount
            ),

            "invoice_currency": (
                invoice.currency
                if invoice
                else None
            ),

            "payment_id": payment_id,

            "payment_invoice_reference": (
                payment_invoice_reference
            ),

            "payment_customer": payment_customer,

            "payment_date": payment_date,

            "payment_amount": payment_amount,

            "payment_currency": payment_currency,

            "gateway_reference": gateway_reference,

            "bank_transaction_id": (
                bank_transaction_id
            ),

            "bank_deposit_date": (
                bank_deposit_date
            ),

            "bank_currency": bank_currency,
        },

        "financial": {

            "original_invoice_amount": (
                case.original_invoice_amount
            ),

            "payment_amount": (
                case.payment_amount
            ),

            "bank_amount": (
                case.bank_amount
            ),

            "payment_fee": (
                case.payment_fee
            ),

            "outstanding_amount": (
                case.outstanding_amount
            ),

            "payment_coverage_percent": (
                case.payment_coverage_percent
            ),

            "bank_payment_difference": (
                case.bank_payment_difference
            ),

            "invoice_payment_difference": (
                case.invoice_payment_difference
            ),

            "financial_status": (
                case.financial_status
            ),

            "financial_impact": (
                case.financial_impact
            ),
        },

        "ai_investigation": {

            "hypothesis": (
                investigation.hypothesis
                if investigation
                else None
            ),

            "confidence": (
                investigation.investigation_confidence
                if investigation
                else None
            ),

            "rationale": (
                investigation.rationale
                if investigation
                else None
            ),

            "finding": (
                investigation.investigation_finding
                if investigation
                else None
            ),

            "likely_cause": (
                investigation.likely_cause
                if investigation
                else None
            ),

            "recommended_action": (
                investigation.recommended_action
                if investigation
                else None
            ),

            "evidence_summary": (
                investigation.evidence_summary
                if investigation
                else None
            ),

            "reasoning_steps": (
                investigation.reasoning_steps
                if investigation
                else None
            ),
        },

        "risk": {

            "level": (
                risk.risk_level
                if risk
                else None
            ),

            "priority_score": (
                risk.priority_score
                if risk
                else None
            ),

            "human_review_required": (
                risk.human_review_required
                if risk
                else None
            ),

            "reason": (
                risk.risk_reason
                if risk
                else None
            ),
        },

        "review": {

            "reviewer_decision": (
                reviewer_decision
            ),

            "reviewer_comment": (
                reviewer_comment
            ),

            "reviewed_at": (
                reviewed_at
            ),

            "final_status": (
                final_status
            ),
        },
    }

    return result