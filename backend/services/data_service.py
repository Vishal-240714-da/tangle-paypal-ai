from sqlalchemy import select

from database.connection import SessionLocal
from database.models import (
    Invoice,
    Payment,
    BankTransaction,
    Case,
    Investigation,
    RiskAssessment,
    Review,
)


def get_db_session():
    return SessionLocal()


def get_all_cases():
    session = get_db_session()

    try:
        return session.scalars(
            select(Case).order_by(Case.case_id)
        ).all()

    finally:
        session.close()


def get_case(case_id):
    session = get_db_session()

    try:
        return session.get(Case, case_id)

    finally:
        session.close()


def get_investigation(case_id):
    session = get_db_session()

    try:
        return session.scalars(
            select(Investigation)
            .where(Investigation.case_id == case_id)
        ).first()

    finally:
        session.close()


def get_risk_assessment(case_id):
    session = get_db_session()

    try:
        return session.scalars(
            select(RiskAssessment)
            .where(RiskAssessment.case_id == case_id)
        ).first()

    finally:
        session.close()


def get_review(case_id):
    session = get_db_session()

    try:
        return session.scalars(
            select(Review)
            .where(Review.case_id == case_id)
        ).first()

    finally:
        session.close()


def get_all_reviews():
    session = get_db_session()

    try:
        return session.scalars(
            select(Review).order_by(Review.id)
        ).all()

    finally:
        session.close()


def get_invoice(invoice_id):
    session = get_db_session()

    try:
        return session.get(Invoice, invoice_id)

    finally:
        session.close()


def get_payment(payment_id):
    session = get_db_session()

    try:
        return session.get(Payment, payment_id)

    finally:
        session.close()


def get_bank_transaction(bank_transaction_id):
    session = get_db_session()

    try:
        return session.get(
            BankTransaction,
            bank_transaction_id,
        )

    finally:
        session.close()


def load_master_data():
    """
    Compatibility function for the existing Cases API.

    Converts PostgreSQL Case records into a pandas DataFrame
    so existing route logic can continue working.
    """

    import pandas as pd

    cases = get_all_cases()

    if not cases:
        return pd.DataFrame()

    records = []

    for case in cases:
        records.append({
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
        })

    return pd.DataFrame(records)