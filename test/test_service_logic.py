import pandas as pd
import pytest

from agents.decision_engine import make_decision
from agents.exception_detector import (
    amounts_match,
    detect_exception,
)
from agents.risk_engine import calculate_risk
from backend.services.audit_service import derive_audit_action

from backend.services.data_quality_service import (
    _is_missing,
    _record_id,
    _validate_dataframe_structure,
    _validate_amounts,
    _validate_dates,
    _validate_currencies,
)

from backend.services.reconciliation_service import (
    _calculate_coverage,
    _clean_id,
    _clean_text,
    _safe_float,
    _build_record,
)

from agents.decision_engine import make_decision

from agents.exception_detector import detect_exception

from agents.risk_engine import calculate_risk


# ============================================================
# AUDIT SERVICE
# ============================================================


def test_audit_case_created_action():
    result = derive_audit_action(
        None,
        "PENDING_REVIEW",
        None,
    )

    assert result == "CASE_CREATED"


def test_audit_investigation_started_action():
    result = derive_audit_action(
        "PENDING_REVIEW",
        "INVESTIGATING",
        None,
    )

    assert result == "INVESTIGATION_STARTED"


def test_audit_submitted_for_review_action():
    result = derive_audit_action(
        "INVESTIGATING",
        "PENDING_REVIEW",
        None,
    )

    assert result == "SUBMITTED_FOR_REVIEW"


def test_audit_human_review_action():
    result = derive_audit_action(
        "PENDING_REVIEW",
        "APPROVED",
        "Completed HUMAN REVIEW",
    )

    assert result == "HUMAN_REVIEW"


def test_audit_approved_action():
    result = derive_audit_action(
        "PENDING_REVIEW",
        "APPROVED",
        None,
    )

    assert result == "CASE_APPROVED"


def test_audit_rejected_action():
    result = derive_audit_action(
        "PENDING_REVIEW",
        "REJECTED",
        None,
    )

    assert result == "CASE_REJECTED"


def test_audit_escalated_action():
    result = derive_audit_action(
        "PENDING_REVIEW",
        "ESCALATED",
        None,
    )

    assert result == "CASE_ESCALATED"


def test_audit_resolved_action():
    result = derive_audit_action(
        "ESCALATED",
        "RESOLVED",
        None,
    )

    assert result == "CASE_RESOLVED"


def test_audit_unknown_transition_returns_status_changed():
    result = derive_audit_action(
        "INVESTIGATING",
        "CUSTOM_STATUS",
        None,
    )

    assert result == "STATUS_CHANGED"


# ============================================================
# DECISION ENGINE
# ============================================================


def test_decision_full_reconciliation():
    result = make_decision(
        {
            "category": "FULL_RECONCILIATION",
            "confidence": 0.98,
        }
    )

    assert result["decision"] == "RECONCILE"
    assert result["confidence"] == 0.98
    assert "match" in result["reason"].lower()


def test_decision_fee_adjusted_reconciliation():
    result = make_decision(
        {
            "category": "FEE_ADJUSTED_RECONCILIATION",
            "confidence": 0.96,
        }
    )

    assert result["decision"] == "RECONCILE"


def test_decision_partial_payment():
    result = make_decision(
        {
            "category": "PARTIAL_PAYMENT",
            "confidence": 0.97,
        }
    )

    assert result["decision"] == "INVESTIGATE"


def test_decision_overpayment():
    result = make_decision(
        {
            "category": "OVERPAYMENT",
            "confidence": 0.97,
        }
    )

    assert result["decision"] == "INVESTIGATE"


def test_decision_missing_payment():
    result = make_decision(
        {
            "category": "MISSING_PAYMENT",
            "confidence": 0.90,
        }
    )

    assert result["decision"] == "INVESTIGATE"


def test_decision_missing_bank_transaction():
    result = make_decision(
        {
            "category": "MISSING_BANK_TRANSACTION",
            "confidence": 0.90,
        }
    )

    assert result["decision"] == "INVESTIGATE"


def test_decision_bank_payment_mismatch():
    result = make_decision(
        {
            "category": "BANK_PAYMENT_MISMATCH",
            "confidence": 0.95,
        }
    )

    assert result["decision"] == "INVESTIGATE"


def test_decision_multi_invoice_payment():
    result = make_decision(
        {
            "category": "MULTI_INVOICE_PAYMENT",
            "confidence": 0.95,
        }
    )

    assert result["decision"] == "INVESTIGATE"


def test_decision_unknown_category_escalates():
    result = make_decision(
        {
            "category": "NOT_A_REAL_CATEGORY",
            "confidence": 0.50,
        }
    )

    assert result["decision"] == "ESCALATE"


def test_decision_none_input_escalates():
    result = make_decision(None)

    assert result["decision"] == "ESCALATE"
    assert result["confidence"] == 0.0


# ============================================================
# EXCEPTION DETECTOR
# ============================================================


def test_amounts_match_within_tolerance():
    assert amounts_match(100.00, 100.005)


def test_amounts_match_exact_values():
    assert amounts_match(1000, 1000)


def test_amounts_do_not_match():
    assert not amounts_match(100.00, 100.10)


def test_amounts_match_rejects_missing_value():
    assert not amounts_match(None, 100)


def test_exception_missing_payment():
    result = detect_exception(
        invoice={
            "invoice_id": "INV-001",
            "amount": 1000,
        },
        payment=None,
        bank=None,
    )

    assert result["category"] == "MISSING_PAYMENT"
    assert result["suggested_action"] == "INVESTIGATE"
    assert result["confidence"] == 0.90


def test_exception_missing_bank_transaction():
    result = detect_exception(
        invoice={
            "invoice_id": "INV-001",
            "amount": 1000,
        },
        payment={
            "payment_id": "PAY-001",
            "amount": 1000,
        },
        bank=None,
    )

    assert result["category"] == "MISSING_BANK_TRANSACTION"
    assert result["suggested_action"] == "INVESTIGATE"


def test_exception_bank_payment_mismatch():
    result = detect_exception(
        invoice={
            "invoice_id": "INV-001",
            "amount": 1000,
        },
        payment={
            "payment_id": "PAY-001",
            "amount": 1000,
        },
        bank={
            "bank_transaction_id": "BANK-001",
            "amount": 900,
        },
    )

    assert result["category"] == "BANK_PAYMENT_MISMATCH"
    assert result["suggested_action"] == "INVESTIGATE"


def test_exception_full_reconciliation():
    result = detect_exception(
        invoice={
            "invoice_id": "INV-001",
            "amount": 1000,
        },
        payment={
            "payment_id": "PAY-001",
            "amount": 1000,
            "fee": 0,
        },
        bank={
            "bank_transaction_id": "BANK-001",
            "amount": 1000,
        },
    )

    assert result["category"] == "FULL_RECONCILIATION"
    assert result["suggested_action"] == "RECONCILE"
    assert result["confidence"] == 0.98


def test_exception_fee_adjusted_reconciliation():
    result = detect_exception(
        invoice={
            "invoice_id": "INV-001",
            "amount": 1000,
        },
        payment={
            "payment_id": "PAY-001",
            "amount": 972.39,
            "fee": 27.61,
        },
        bank={
            "bank_transaction_id": "BANK-001",
            "amount": 972.39,
        },
    )

    assert result["category"] == "FEE_ADJUSTED_RECONCILIATION"
    assert result["suggested_action"] == "RECONCILE"


def test_exception_partial_payment():
    result = detect_exception(
        invoice={
            "invoice_id": "INV-001",
            "amount": 1000,
        },
        payment={
            "payment_id": "PAY-001",
            "amount": 700,
        },
        bank={
            "bank_transaction_id": "BANK-001",
            "amount": 700,
        },
    )

    assert result["category"] == "PARTIAL_PAYMENT"
    assert result["suggested_action"] == "INVESTIGATE"


def test_exception_overpayment():
    result = detect_exception(
        invoice={
            "invoice_id": "INV-001",
            "amount": 1000,
        },
        payment={
            "payment_id": "PAY-001",
            "amount": 1200,
        },
        bank={
            "bank_transaction_id": "BANK-001",
            "amount": 1200,
        },
    )

    assert result["category"] == "OVERPAYMENT"
    assert result["suggested_action"] == "INVESTIGATE"


def test_exception_unknown_pattern():
    result = detect_exception(
        invoice=None,
        payment=None,
        bank=None,
    )

    assert result["category"] == "UNKNOWN"
    assert result["suggested_action"] == "ESCALATE"


# ============================================================
# RISK ENGINE
# ============================================================


def test_risk_full_reconciliation_is_low():
    result = calculate_risk(
        {
            "category": "FULL_RECONCILIATION",
            "invoice_amount": 1500,
            "payment_amount": 1500,
            "bank_amount": 1500,
            "outstanding_amount": 0,
            "payment_coverage_percent": 100,
            "confidence": 0.98,
        }
    )

    assert result["risk_level"] == "LOW"
    assert result["priority_score"] == 5
    assert result["human_review_required"] is False


def test_risk_partial_payment_is_medium():
    result = calculate_risk(
        {
            "category": "PARTIAL_PAYMENT",
            "invoice_amount": 1500,
            "payment_amount": 1200,
            "bank_amount": 1200,
            "outstanding_amount": 300,
            "payment_coverage_percent": 80,
            "confidence": 0.97,
        }
    )

    assert result["risk_level"] == "MEDIUM"
    assert result["priority_score"] == 60
    assert result["human_review_required"] is False


def test_risk_severe_partial_payment():
    result = calculate_risk(
        {
            "category": "PARTIAL_PAYMENT",
            "invoice_amount": 5000,
            "payment_amount": 2000,
            "bank_amount": 2000,
            "outstanding_amount": 3000,
            "payment_coverage_percent": 40,
            "confidence": 0.97,
        }
    )

    assert result["priority_score"] == 80
    assert result["risk_level"] == "HIGH"
    assert result["human_review_required"] is True


def test_risk_bank_payment_mismatch_is_high():
    result = calculate_risk(
        {
            "category": "BANK_PAYMENT_MISMATCH",
            "invoice_amount": 10000,
            "payment_amount": 10000,
            "bank_amount": 9000,
            "outstanding_amount": 0,
            "payment_coverage_percent": 100,
            "confidence": 0.95,
        }
    )

    assert result["risk_level"] == "HIGH"
    assert result["priority_score"] == 75
    assert result["human_review_required"] is True


def test_risk_missing_payment_is_high():
    result = calculate_risk(
        {
            "category": "MISSING_PAYMENT",
            "invoice_amount": 10000,
            "payment_amount": 0,
            "bank_amount": 0,
            "outstanding_amount": 10000,
            "payment_coverage_percent": 0,
            "confidence": 0.90,
        }
    )

    assert result["risk_level"] == "HIGH"
    assert result["priority_score"] == 80
    assert result["human_review_required"] is True


def test_risk_unknown_case_is_critical():
    result = calculate_risk(
        {
            "category": "UNKNOWN",
            "confidence": 0.50,
        }
    )

    assert result["risk_level"] == "CRITICAL"
    assert result["priority_score"] == 100
    assert result["human_review_required"] is True


def test_risk_low_confidence_increases_score():
    result = calculate_risk(
        {
            "category": "FULL_RECONCILIATION",
            "confidence": 0.50,
        }
    )

    assert result["priority_score"] == 15
    assert result["risk_level"] == "LOW"


def test_risk_score_is_capped_at_100():
    result = calculate_risk(
        {
            "category": "MISSING_PAYMENT",
            "bank_amount": 20000,
            "confidence": 0.50,
        }
    )

    assert result["priority_score"] <= 100


# ============================================================
# DATA QUALITY HELPERS
# ============================================================


def test_data_quality_detects_missing_required_column():
    df = pd.DataFrame(
        {
            "invoice_id": ["INV-001"],
            "amount": [1000],
        }
    )

    issues = _validate_dataframe_structure(
        df=df,
        dataset="invoices",
        required_columns=[
            "invoice_id",
            "amount",
            "currency",
        ],
        id_column="invoice_id",
    )

    assert len(issues) == 1
    assert issues[0].issue_type == "MALFORMED_RECORD"
    assert issues[0].severity == "ERROR"


def test_data_quality_detects_missing_id():
    df = pd.DataFrame(
        {
            "invoice_id": [None],
            "amount": [1000],
            "currency": ["INR"],
        }
    )

    issues = _validate_dataframe_structure(
        df=df,
        dataset="invoices",
        required_columns=[
            "invoice_id",
            "amount",
            "currency",
        ],
        id_column="invoice_id",
    )

    assert any(
        issue.issue_type == "MISSING_ID"
        for issue in issues
    )


def test_data_quality_detects_duplicate_id():
    df = pd.DataFrame(
        {
            "invoice_id": [
                "INV-001",
                "INV-001",
            ],
            "amount": [
                1000,
                2000,
            ],
        }
    )

    issues = _validate_dataframe_structure(
        df=df,
        dataset="invoices",
        required_columns=[
            "invoice_id",
            "amount",
        ],
        id_column="invoice_id",
    )

    assert any(
        issue.issue_type == "DUPLICATE_RECORD"
        for issue in issues
    )


def test_data_quality_detects_negative_amount():
    df = pd.DataFrame(
        {
            "invoice_id": ["INV-001"],
            "amount": [-100],
        }
    )

    issues = _validate_amounts(
        df=df,
        dataset="invoices",
        id_column="invoice_id",
        amount_columns=["amount"],
    )

    assert len(issues) == 1
    assert issues[0].issue_type == "NEGATIVE_VALUE"
    assert issues[0].severity == "ERROR"


def test_data_quality_detects_invalid_amount():
    df = pd.DataFrame(
        {
            "invoice_id": ["INV-001"],
            "amount": ["not-a-number"],
        }
    )

    issues = _validate_amounts(
        df=df,
        dataset="invoices",
        id_column="invoice_id",
        amount_columns=["amount"],
    )

    assert len(issues) == 1
    assert issues[0].issue_type == "INVALID_AMOUNT"


def test_data_quality_detects_missing_amount():
    df = pd.DataFrame(
        {
            "invoice_id": ["INV-001"],
            "amount": [None],
        }
    )

    issues = _validate_amounts(
        df=df,
        dataset="invoices",
        id_column="invoice_id",
        amount_columns=["amount"],
    )

    assert len(issues) == 1
    assert issues[0].issue_type == "INVALID_AMOUNT"


def test_data_quality_detects_invalid_date():
    df = pd.DataFrame(
        {
            "invoice_id": ["INV-001"],
            "invoice_date": ["not-a-date"],
        }
    )

    issues = _validate_dates(
        df=df,
        dataset="invoices",
        id_column="invoice_id",
        date_columns=["invoice_date"],
    )

    assert len(issues) == 1
    assert issues[0].issue_type == "INVALID_DATE"


def test_data_quality_detects_missing_date():
    df = pd.DataFrame(
        {
            "invoice_id": ["INV-001"],
            "invoice_date": [None],
        }
    )

    issues = _validate_dates(
        df=df,
        dataset="invoices",
        id_column="invoice_id",
        date_columns=["invoice_date"],
    )

    assert len(issues) == 1
    assert issues[0].issue_type == "INVALID_DATE"


def test_data_quality_missing_currency_is_warning():
    df = pd.DataFrame(
        {
            "invoice_id": ["INV-001"],
            "currency": [None],
        }
    )

    issues = _validate_currencies(
        df=df,
        dataset="invoices",
        id_column="invoice_id",
    )

    assert len(issues) == 1
    assert issues[0].issue_type == "CURRENCY_PROBLEM"
    assert issues[0].severity == "WARNING"


def test_data_quality_unsupported_currency_is_warning():
    df = pd.DataFrame(
        {
            "invoice_id": ["INV-001"],
            "currency": ["XYZ"],
        }
    )

    issues = _validate_currencies(
        df=df,
        dataset="invoices",
        id_column="invoice_id",
    )

    assert len(issues) == 1
    assert issues[0].issue_type == "CURRENCY_PROBLEM"
    assert issues[0].severity == "WARNING"


def test_data_quality_supported_currency_has_no_issue():
    df = pd.DataFrame(
        {
            "invoice_id": ["INV-001"],
            "currency": ["INR"],
        }
    )

    issues = _validate_currencies(
        df=df,
        dataset="invoices",
        id_column="invoice_id",
    )

    assert issues == []


def test_data_quality_coverage_calculation():
    result = _calculate_coverage(
        invoice_amount=1000,
        payment_amount=750,
    )

    assert result == 75.0


def test_data_quality_coverage_zero_invoice_returns_none():
    result = _calculate_coverage(
        invoice_amount=0,
        payment_amount=500,
    )

    assert result is None


# ============================================================
# RECONCILIATION HELPERS
# ============================================================


def test_reconciliation_clean_id():
    assert _clean_id("  INV-001  ") == "INV-001"


def test_reconciliation_clean_empty_id():
    assert _clean_id("   ") is None


def test_reconciliation_clean_text():
    assert _clean_text("  EXACT  ") == "EXACT"


def test_reconciliation_clean_empty_text():
    assert _clean_text("") is None


def test_reconciliation_safe_float():
    assert _safe_float("1250.50") == 1250.50


def test_reconciliation_safe_float_invalid_value():
    assert _safe_float("not-a-number") is None


def test_reconciliation_coverage_calculation():
    result = _calculate_coverage(
        1000,
        800,
    )

    assert result == 80.0


def test_reconciliation_coverage_missing_amount():
    result = _calculate_coverage(
        None,
        800,
    )

    assert result is None


def test_reconciliation_build_record_calculates_differences():
    invoices = {
        "INV-001": {
            "amount": 1000,
            "currency": "INR",
            "invoice_date": "2026-01-01",
        }
    }

    payments = {
        "PAY-001": {
            "amount": 800,
            "currency": "INR",
            "payment_date": "2026-01-02",
        }
    }

    banks = {
        "BANK-001": {
            "amount": 800,
            "currency": "INR",
            "deposit_date": "2026-01-03",
        }
    }

    result = _build_record(
        {
            "invoice_id": "INV-001",
            "payment_id": "PAY-001",
            "bank_transaction_id": "BANK-001",
            "pass": 0,
            "match_type": "FUZZY",
            "confidence": 0.85,
            "rationale": "Partial payment.",
        },
        invoices,
        payments,
        banks,
    )

    assert result.invoice_id == "INV-001"
    assert result.payment_id == "PAY-001"
    assert result.bank_transaction_id == "BANK-001"
    assert result.invoice_amount == 1000.0
    assert result.payment_amount == 800.0
    assert result.bank_amount == 800.0
    assert result.payment_invoice_difference == -200.0
    assert result.bank_payment_difference == 0.0
    assert result.payment_coverage_percent == 80.0
    assert result.match_type == "FUZZY"