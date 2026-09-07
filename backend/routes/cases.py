from fastapi import APIRouter, HTTPException

from backend.services.data_service import (
    get_all_cases,
    get_case,
)


router = APIRouter(
    prefix="/api/cases",
    tags=["Cases"],
)


@router.get("")
def get_cases():

    cases = get_all_cases()

    if not cases:
        return []

    return [
        {
            "case_id": case.case_id,
            "record_type": case.record_type,
            "record_id": case.record_id,
            "invoice_id": case.invoice_id,
            "category": case.category,
            "confidence": case.confidence,
            "suggested_action": case.suggested_action,
            "reason": case.reason,
            "next_action": case.next_action,
            "payment_amount": case.payment_amount,
            "bank_amount": case.bank_amount,
            "payment_fee": case.payment_fee,
            "outstanding_amount": case.outstanding_amount,
            "payment_coverage_percent": case.payment_coverage_percent,
            "bank_payment_difference": case.bank_payment_difference,
            "invoice_payment_difference": case.invoice_payment_difference,
            "financial_status": case.financial_status,
            "financial_impact": case.financial_impact,
            "original_invoice_amount": case.original_invoice_amount,
            "decision": case.decision,
            "decision_confidence": case.decision_confidence,
            "related_invoice_count": case.related_invoice_count,
            "related_invoice_ids": case.related_invoice_ids,
        }
        for case in cases
    ]


@router.get("/{case_id}")
def get_case_by_id(case_id: str):

    case_id = case_id.strip()

    case = get_case(case_id)

    if case is None:
        raise HTTPException(
            status_code=404,
            detail=f"Case {case_id} not found.",
        )

    return {
        "case_id": case.case_id,
        "record_type": case.record_type,
        "record_id": case.record_id,
        "invoice_id": case.invoice_id,
        "category": case.category,
        "confidence": case.confidence,
        "suggested_action": case.suggested_action,
        "reason": case.reason,
        "next_action": case.next_action,
        "payment_amount": case.payment_amount,
        "bank_amount": case.bank_amount,
        "payment_fee": case.payment_fee,
        "outstanding_amount": case.outstanding_amount,
        "payment_coverage_percent": case.payment_coverage_percent,
        "bank_payment_difference": case.bank_payment_difference,
        "invoice_payment_difference": case.invoice_payment_difference,
        "financial_status": case.financial_status,
        "financial_impact": case.financial_impact,
        "original_invoice_amount": case.original_invoice_amount,
        "decision": case.decision,
        "decision_confidence": case.decision_confidence,
        "related_invoice_count": case.related_invoice_count,
        "related_invoice_ids": case.related_invoice_ids,
    }