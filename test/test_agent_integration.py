import pytest

from agents.case_lifecycle import (
    VALID_STATUSES,
    ALLOWED_TRANSITIONS,
    is_valid_status,
    can_transition,
    transition_case,
    get_next_statuses,
    get_lifecycle_description,
)

from agents.decision_engine import make_decision

from agents.exception_detector import detect_exception

from agents.agent import (
    calculate_financial_metrics,
    generate_investigation_finding,
    generate_likely_cause,
    generate_recommended_action,
    generate_reasoning_steps,
    generate_evidence_summary,
    calculate_financial_impact,
    investigate,
)

from agents.tools import (
    calculate_difference,
    calculate_fx,
    analyze_fee,
)


# ============================================================
# CASE LIFECYCLE INTEGRATION
# ============================================================


def test_complete_case_lifecycle_path():
    assert can_transition(
        "OPEN",
        "INVESTIGATING",
    )

    assert can_transition(
        "INVESTIGATING",
        "PENDING_REVIEW",
    )

    assert can_transition(
        "PENDING_REVIEW",
        "APPROVED",
    )

    assert can_transition(
        "APPROVED",
        "RESOLVED",
    )


def test_rejected_case_lifecycle_path():
    assert can_transition(
        "OPEN",
        "INVESTIGATING",
    )

    assert can_transition(
        "INVESTIGATING",
        "PENDING_REVIEW",
    )

    assert can_transition(
        "PENDING_REVIEW",
        "REJECTED",
    )

    assert can_transition(
        "REJECTED",
        "RESOLVED",
    )


def test_escalated_case_can_return_to_investigation():
    assert can_transition(
        "PENDING_REVIEW",
        "ESCALATED",
    )

    assert can_transition(
        "ESCALATED",
        "INVESTIGATING",
    )

    assert can_transition(
        "INVESTIGATING",
        "PENDING_REVIEW",
    )


def test_escalated_case_can_be_resolved():
    assert can_transition(
        "ESCALATED",
        "RESOLVED",
    )


def test_resolved_case_is_terminal():
    assert get_next_statuses("RESOLVED") == []

    assert not can_transition(
        "RESOLVED",
        "INVESTIGATING",
    )

    assert not can_transition(
        "RESOLVED",
        "OPEN",
    )


def test_invalid_lifecycle_status():
    assert not is_valid_status("INVALID")

    assert get_next_statuses("INVALID") == []


def test_invalid_lifecycle_transition():
    result = transition_case(
        "OPEN",
        "APPROVED",
    )

    assert result["success"] is False
    assert result["previous_status"] == "OPEN"
    assert result["new_status"] == "APPROVED"


def test_valid_lifecycle_transition_result():
    result = transition_case(
        "OPEN",
        "INVESTIGATING",
    )

    assert result["success"] is True
    assert result["previous_status"] == "OPEN"
    assert result["new_status"] == "INVESTIGATING"


def test_lifecycle_description_contains_all_statuses():
    description = get_lifecycle_description()

    for status in VALID_STATUSES:
        assert status in description

    assert description["OPEN"] == ["INVESTIGATING"]
    assert description["INVESTIGATING"] == ["PENDING_REVIEW"]
    assert set(description["PENDING_REVIEW"]) == {
        "APPROVED",
        "REJECTED",
        "ESCALATED",
    }


# ============================================================
# EXCEPTION → DECISION INTEGRATION
# ============================================================


def test_full_reconciliation_exception_to_decision():
    exception = detect_exception(
        invoice={
            "amount": 1000,
        },
        payment={
            "amount": 1000,
        },
        bank={
            "amount": 1000,
        },
    )

    assert exception["category"] == "FULL_RECONCILIATION"

    decision = make_decision(exception)

    assert decision["decision"] == "RECONCILE"
    assert decision["next_action"] == "Close the reconciliation case."


def test_partial_payment_exception_to_decision():
    exception = detect_exception(
        invoice={
            "amount": 1000,
        },
        payment={
            "amount": 600,
        },
        bank={
            "amount": 600,
        },
    )

    assert exception["category"] == "PARTIAL_PAYMENT"

    decision = make_decision(exception)

    assert decision["decision"] == "INVESTIGATE"
    assert decision["next_action"] == "Review the outstanding balance and payment status."


def test_overpayment_exception_to_decision():
    exception = detect_exception(
        invoice={
            "amount": 1000,
        },
        payment={
            "amount": 1200,
        },
        bank={
            "amount": 1200,
        },
    )

    assert exception["category"] == "OVERPAYMENT"

    decision = make_decision(exception)

    assert decision["next_action"] == "Review the overpayment and determine whether a refund or adjustment is required."


def test_missing_payment_exception_to_decision():
    exception = detect_exception(
        invoice={
            "amount": 1000,
        },
        payment=None,
        bank=None,
    )

    assert exception["category"] == "MISSING_PAYMENT"

    decision = make_decision(exception)

    assert decision["next_action"] == "Search payment records and verify the customer's payment status."

def test_missing_bank_exception_to_decision():
    exception = detect_exception(
        invoice={
            "amount": 1000,
        },
        payment={
            "amount": 1000,
        },
        bank=None,
    )

    assert exception["category"] == "MISSING_BANK_TRANSACTION"

    decision = make_decision(exception)

    assert decision["decision"] == "INVESTIGATE"


def test_bank_payment_mismatch_to_decision():
    exception = detect_exception(
        invoice={
            "amount": 1000,
        },
        payment={
            "amount": 1000,
        },
        bank={
            "amount": 950,
        },
    )

    assert exception["category"] == "BANK_PAYMENT_MISMATCH"

    decision = make_decision(exception)

    assert decision["decision"] == "INVESTIGATE"


# ============================================================
# INVESTIGATION AGENT INTEGRATION
# ============================================================


def test_investigation_full_reconciliation():
    result = investigate(
        {
            "record_id": "TEST-FULL-001",
            "invoice_id": "INV-001",
            "payment_id": "PAY-001",
            "bank_transaction_id": "BANK-001",
            "invoice_amount": 1000,
            "payment_amount": 1000,
            "payment_fee": 0,
            "bank_amount": 1000,
            "category": "FULL_RECONCILIATION",
            "confidence": 0.98,
        }
    )

    assert result["category"] == "FULL_RECONCILIATION"
    assert result["confidence"] == 0.98
    assert result["risk_level"] == "LOW"
    assert result["priority_score"] == 5
    assert result["human_review_required"] is False
    assert result["financial_metrics"]["financial_status"] == "FULLY_PAID"
    assert result["financial_impact"] == "NO_OUTSTANDING_BALANCE"
    assert len(result["reasoning_steps"]) > 0
    assert result["evidence_summary"]


def test_investigation_partial_payment():
    result = investigate(
        {
            "record_id": "TEST-PARTIAL-001",
            "invoice_id": "INV-002",
            "payment_id": "PAY-002",
            "bank_transaction_id": "BANK-002",
            "invoice_amount": 1000,
            "payment_amount": 600,
            "payment_fee": 0,
            "bank_amount": 600,
            "category": "PARTIAL_PAYMENT",
            "confidence": 0.97,
        }
    )

    assert result["category"] == "PARTIAL_PAYMENT"
    assert result["financial_metrics"]["payment_coverage_percent"] == 60.0
    assert result["financial_metrics"]["outstanding_amount"] == 400.0
    assert result["financial_impact"] == "OUTSTANDING_BALANCE_400.00"
    assert result["risk_level"] == "HIGH"
    assert result["priority_score"] == 70
    assert result["human_review_required"] is True
    assert len(result["reasoning_steps"]) >= 5


def test_investigation_severe_partial_payment():
    result = investigate(
        {
            "record_id": "TEST-PARTIAL-002",
            "invoice_id": "INV-003",
            "payment_id": "PAY-003",
            "bank_transaction_id": "BANK-003",
            "invoice_amount": 5000,
            "payment_amount": 2000,
            "payment_fee": 0,
            "bank_amount": 2000,
            "category": "PARTIAL_PAYMENT",
            "confidence": 0.97,
        }
    )

    assert result["financial_metrics"]["payment_coverage_percent"] == 40.0
    assert result["financial_metrics"]["outstanding_amount"] == 3000.0
    assert result["risk_level"] == "HIGH"
    assert result["priority_score"] == 80
    assert result["human_review_required"] is True


def test_investigation_overpayment():
    result = investigate(
        {
            "record_id": "TEST-OVER-001",
            "invoice_id": "INV-004",
            "payment_id": "PAY-004",
            "bank_transaction_id": "BANK-004",
            "invoice_amount": 1000,
            "payment_amount": 1200,
            "payment_fee": 0,
            "bank_amount": 1200,
            "category": "OVERPAYMENT",
            "confidence": 0.96,
        }
    )

    assert result["category"] == "OVERPAYMENT"
    assert result["financial_metrics"]["financial_status"] == "OVERPAID"
    assert result["financial_impact"] == "OVERPAYMENT_200.00"
    assert result["risk_level"] == "MEDIUM"
    assert result["human_review_required"] is False


def test_investigation_bank_payment_mismatch():
    result = investigate(
        {
            "record_id": "TEST-MISMATCH-001",
            "invoice_id": "INV-005",
            "payment_id": "PAY-005",
            "bank_transaction_id": "BANK-005",
            "invoice_amount": 1000,
            "payment_amount": 1000,
            "payment_fee": 0,
            "bank_amount": 950,
            "category": "BANK_PAYMENT_MISMATCH",
            "confidence": 0.95,
        }
    )

    assert result["category"] == "BANK_PAYMENT_MISMATCH"
    assert result["financial_metrics"]["bank_payment_difference"] == -50.0
    assert result["risk_level"] == "HIGH"
    assert result["priority_score"] == 75
    assert result["human_review_required"] is True


def test_investigation_missing_bank_transaction():
    result = investigate(
        {
            "record_id": "TEST-MISSING-BANK-001",
            "invoice_id": "INV-006",
            "payment_id": "PAY-006",
            "invoice_amount": 1000,
            "payment_amount": 1000,
            "payment_fee": 0,
            "bank_amount": None,
            "category": "MISSING_BANK_TRANSACTION",
            "confidence": 0.95,
        }
    )

    assert result["category"] == "MISSING_BANK_TRANSACTION"
    assert result["risk_level"] == "HIGH"
    assert result["priority_score"] == 80
    assert result["human_review_required"] is True


def test_investigation_missing_payment():
    result = investigate(
        {
            "record_id": "TEST-MISSING-PAYMENT-001",
            "invoice_id": "INV-007",
            "payment_id": None,
            "bank_transaction_id": None,
            "invoice_amount": 1000,
            "payment_amount": None,
            "payment_fee": 0,
            "bank_amount": None,
            "category": "MISSING_PAYMENT",
            "confidence": 0.95,
        }
    )

    assert result["category"] == "MISSING_PAYMENT"
    assert result["risk_level"] == "HIGH"
    assert result["priority_score"] == 80
    assert result["human_review_required"] is True


# ============================================================
# INVESTIGATION OUTPUT STRUCTURE
# ============================================================


def test_investigation_contains_complete_explainability_output():
    result = investigate(
        {
            "record_id": "TEST-EXPLAIN-001",
            "invoice_id": "INV-008",
            "payment_id": "PAY-008",
            "bank_transaction_id": "BANK-008",
            "invoice_amount": 1000,
            "payment_amount": 800,
            "payment_fee": 0,
            "bank_amount": 800,
            "category": "PARTIAL_PAYMENT",
            "confidence": 0.90,
        }
    )

    required_fields = {
        "hypothesis",
        "confidence",
        "category",
        "rationale",
        "suggested_action",
        "investigation_finding",
        "likely_cause",
        "recommended_action",
        "financial_metrics",
        "reasoning_steps",
        "evidence_summary",
        "financial_impact",
        "risk_level",
        "priority_score",
        "human_review_required",
        "risk_reason",
    }

    assert required_fields.issubset(result.keys())
    assert len(result["reasoning_steps"]) > 0
    assert result["investigation_finding"]
    assert result["likely_cause"]
    assert result["recommended_action"]
    assert result["risk_reason"]


# ============================================================
# FINANCIAL METRICS → INVESTIGATION INTELLIGENCE
# ============================================================


def test_financial_metrics_feed_investigation_helpers():
    metrics = calculate_financial_metrics(
        invoice_amount=1000,
        payment_amount=750,
        bank_amount=750,
        payment_fee=0,
    )

    assert metrics["outstanding_amount"] == 250.0
    assert metrics["payment_coverage_percent"] == 75.0
    assert metrics["bank_payment_difference"] == 0.0
    assert metrics["financial_status"] == "PARTIALLY_PAID"

    finding = generate_investigation_finding(
        "PARTIAL_PAYMENT",
        metrics,
    )

    cause = generate_likely_cause(
        "PARTIAL_PAYMENT",
        metrics,
    )

    action = generate_recommended_action(
        "PARTIAL_PAYMENT",
        metrics,
    )

    reasoning = generate_reasoning_steps(
        "PARTIAL_PAYMENT",
        metrics,
        invoice_id="INV-TEST",
        payment_id="PAY-TEST",
        bank_id="BANK-TEST",
    )

    evidence = generate_evidence_summary(
        "PARTIAL_PAYMENT",
        metrics,
    )

    impact = calculate_financial_impact(
        metrics,
    )

    assert "750.00" in finding
    assert "75.00%" in finding
    assert cause
    assert action
    assert len(reasoning) > 0
    assert "Invoice amount: 1000.00" in evidence
    assert impact == "OUTSTANDING_BALANCE_250.00"


# ============================================================
# INVESTIGATION TOOLS
# ============================================================


def test_calculate_difference_tool():
    result = calculate_difference(
        expected_amount=1000,
        actual_amount=850,
    )

    assert result["expected_amount"] == 1000.0
    assert result["actual_amount"] == 850.0
    assert result["difference"] == -150.0
    assert result["percentage_difference"] == 15.0


def test_calculate_difference_zero_expected():
    result = calculate_difference(
        expected_amount=0,
        actual_amount=100,
    )

    assert result["difference"] == 100.0
    assert result["percentage_difference"] == 0


def test_calculate_fx_same_currency():
    result = calculate_fx(
        amount=1000,
        from_currency="INR",
        to_currency="INR",
    )

    assert result["amount"] == 1000.0
    assert result["rate"] == 1
    assert result["converted_amount"] == 1000.0


def test_calculate_fx_usd_to_inr():
    result = calculate_fx(
        amount=100,
        from_currency="USD",
        to_currency="INR",
    )

    assert result["rate"] == 83.0
    assert result["converted_amount"] == 8300.0


def test_calculate_fx_unknown_rate():
    result = calculate_fx(
        amount=100,
        from_currency="GBP",
        to_currency="INR",
    )

    assert result["error"] == "FX rate unavailable."


def test_analyze_fee():
    result = analyze_fee(
        invoice_amount=1000,
        payment_amount=975,
    )

    assert result["possible_fee"] == 25.0
    assert result["fee_percentage"] == 2.5
    assert result["looks_like_processing_fee"] is True