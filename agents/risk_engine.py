"""
TANGLE Risk Engine

Evaluates financial investigation cases and assigns:
- Risk level
- Priority score
- Human review requirement
- Risk reason

This module does not make the final business decision.
The decision engine remains responsible for RECONCILE / INVESTIGATE / ESCALATE.
"""


def safe_float(value, default=0.0):
    """Safely convert a value to float."""
    try:
        if value is None:
            return default

        return float(value)

    except (ValueError, TypeError):
        return default


def calculate_risk(case):
    """
    Calculate risk information for an investigated financial case.

    Expected case fields:
    - category
    - outstanding_amount
    - payment_coverage_percent
    - financial_status
    - invoice_amount
    - payment_amount
    - bank_amount
    - confidence
    """

    if case is None:
        case = {}

    category = case.get("category", "UNKNOWN")

    outstanding = safe_float(
        case.get("outstanding_amount")
    )

    coverage = case.get(
        "payment_coverage_percent"
    )

    coverage = (
        safe_float(coverage)
        if coverage is not None
        else None
    )

    invoice_amount = safe_float(
        case.get("invoice_amount")
    )

    payment_amount = safe_float(
        case.get("payment_amount")
    )

    bank_amount = safe_float(
        case.get("bank_amount")
    )

    confidence = safe_float(
        case.get("confidence")
    )

    # ---------------------------------------------------------
    # BASE RISK
    # ---------------------------------------------------------

    risk_score = 0
    risk_reasons = []

    if category == "FULL_RECONCILIATION":

        risk_score = 5

        risk_reasons.append(
            "Invoice, payment and bank records are reconciled."
        )

    elif category == "FEE_ADJUSTED_RECONCILIATION":

        risk_score = 10

        risk_reasons.append(
            "Transaction reconciles after accounting for a payment fee."
        )

    elif category == "PARTIAL_PAYMENT":

        risk_score = 50

        risk_reasons.append(
            "Payment does not fully cover the invoice."
        )

        if coverage is not None:

            if coverage < 50:
                risk_score += 30

                risk_reasons.append(
                    "Payment coverage is below 50%."
                )

            elif coverage < 75:
                risk_score += 20

                risk_reasons.append(
                    "Payment coverage is below 75%."
                )

            elif coverage < 90:
                risk_score += 10

                risk_reasons.append(
                    "Payment coverage is below 90%."
                )

        if outstanding > 10000:

            risk_score += 10

            risk_reasons.append(
                "Outstanding balance exceeds 10,000."
            )

    elif category == "OVERPAYMENT":

        risk_score = 55

        risk_reasons.append(
            "Payment exceeds the invoice amount."
        )

        overpayment = abs(outstanding)

        if overpayment > 10000:

            risk_score += 20

            risk_reasons.append(
                "Overpayment exceeds 10,000."
            )

        elif overpayment > 5000:

            risk_score += 10

            risk_reasons.append(
                "Overpayment exceeds 5,000."
            )

    elif category == "BANK_PAYMENT_MISMATCH":

        risk_score = 75

        risk_reasons.append(
            "Bank transaction amount does not match the payment amount."
        )

    elif category == "MISSING_PAYMENT":

        risk_score = 80

        risk_reasons.append(
            "Expected payment could not be matched."
        )

        if bank_amount > 10000:

            risk_score += 10

            risk_reasons.append(
                "Unmatched bank amount exceeds 10,000."
            )

    elif category == "MISSING_BANK_TRANSACTION":

        risk_score = 80

        risk_reasons.append(
            "Payment exists but the corresponding bank transaction is missing."
        )

        if payment_amount > 10000:

            risk_score += 10

            risk_reasons.append(
                "Unmatched payment exceeds 10,000."
            )

    elif category == "MULTI_INVOICE_PAYMENT":

        risk_score = 60

        risk_reasons.append(
            "A single payment references multiple invoices."
        )

        risk_reasons.append(
            "Payment allocation requires review."
        )

    elif category == "INCOMPLETE_RECONCILIATION":

        risk_score = 65

        risk_reasons.append(
            "Financial records are incomplete."
        )

    else:

        risk_score = 90

        risk_reasons.append(
            "The financial case does not match a known reconciliation pattern."
        )

    # ---------------------------------------------------------
    # CONFIDENCE ADJUSTMENT
    # ---------------------------------------------------------

    if confidence < 0.70:

        risk_score += 10

        risk_reasons.append(
            "Detection confidence is relatively low."
        )

    # ---------------------------------------------------------
    # CAP SCORE
    # ---------------------------------------------------------

    risk_score = min(
        risk_score,
        100
    )

    # ---------------------------------------------------------
    # RISK LEVEL
    # ---------------------------------------------------------

    if risk_score >= 85:

        risk_level = "CRITICAL"

    elif risk_score >= 70:

        risk_level = "HIGH"

    elif risk_score >= 40:

        risk_level = "MEDIUM"

    else:

        risk_level = "LOW"

    # ---------------------------------------------------------
    # HUMAN REVIEW
    # ---------------------------------------------------------

    human_review_required = risk_level in {
        "HIGH",
        "CRITICAL"
    }

    # ---------------------------------------------------------
    # FINAL RISK REASON
    # ---------------------------------------------------------

    risk_reason = " ".join(
        risk_reasons
    )

    return {
        "risk_level": risk_level,
        "priority_score": risk_score,
        "human_review_required": human_review_required,
        "risk_reason": risk_reason
    }


# =============================================================
# TESTS
# =============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("TANGLE RISK ENGINE TEST")
    print("=" * 70)

    test_cases = [

        {
            "name": "Fully Reconciled",
            "case": {
                "category": "FULL_RECONCILIATION",
                "invoice_amount": 1500,
                "payment_amount": 1500,
                "bank_amount": 1500,
                "outstanding_amount": 0,
                "payment_coverage_percent": 100,
                "confidence": 0.98
            }
        },

        {
            "name": "Small Partial Payment",
            "case": {
                "category": "PARTIAL_PAYMENT",
                "invoice_amount": 1500,
                "payment_amount": 1200,
                "bank_amount": 1200,
                "outstanding_amount": 300,
                "payment_coverage_percent": 80,
                "confidence": 0.97
            }
        },

        {
            "name": "Severe Partial Payment",
            "case": {
                "category": "PARTIAL_PAYMENT",
                "invoice_amount": 5000,
                "payment_amount": 2000,
                "bank_amount": 2000,
                "outstanding_amount": 3000,
                "payment_coverage_percent": 40,
                "confidence": 0.97
            }
        },

        {
            "name": "Missing Payment",
            "case": {
                "category": "MISSING_PAYMENT",
                "invoice_amount": None,
                "payment_amount": None,
                "bank_amount": 18500,
                "outstanding_amount": None,
                "payment_coverage_percent": None,
                "confidence": 0.90
            }
        },

        {
            "name": "Missing Bank Transaction",
            "case": {
                "category": "MISSING_BANK_TRANSACTION",
                "invoice_amount": 25000,
                "payment_amount": 25000,
                "bank_amount": None,
                "outstanding_amount": 0,
                "payment_coverage_percent": 100,
                "confidence": 0.90
            }
        },

        {
            "name": "Multi Invoice Payment",
            "case": {
                "category": "MULTI_INVOICE_PAYMENT",
                "invoice_amount": None,
                "payment_amount": 18000,
                "bank_amount": 18000,
                "outstanding_amount": None,
                "payment_coverage_percent": None,
                "confidence": 0.95
            }
        },

        {
            "name": "Unknown Case",
            "case": {
                "category": "UNKNOWN",
                "confidence": 0.50
            }
        }
    ]

    for test in test_cases:

        result = calculate_risk(
            test["case"]
        )

        print()
        print("-" * 70)
        print(
            f"Test: {test['name']}"
        )

        print(
            f"Risk Level: {result['risk_level']}"
        )

        print(
            f"Priority Score: {result['priority_score']}"
        )

        print(
            f"Human Review: "
            f"{result['human_review_required']}"
        )

        print(
            f"Risk Reason: "
            f"{result['risk_reason']}"
        )

    print()
    print("=" * 70)
    print("RISK ENGINE TEST COMPLETE")
    print("=" * 70)