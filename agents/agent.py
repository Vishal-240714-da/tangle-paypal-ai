import json

from agents.risk_engine import calculate_risk


# ============================================================
# BASIC UTILITIES
# ============================================================

def to_float(value):
    """
    Safely convert a value to float.
    Returns None when conversion is not possible.
    """
    try:
        if value is None:
            return None

        return float(value)

    except (ValueError, TypeError):
        return None


# ============================================================
# FINANCIAL METRICS
# ============================================================

def calculate_financial_metrics(
    invoice_amount=None,
    payment_amount=None,
    bank_amount=None,
    payment_fee=None
):
    """
    Calculate financial investigation metrics.

    Returns:
    - outstanding amount
    - payment coverage percentage
    - bank-payment difference
    - invoice-payment difference
    - fee
    - financial status
    """

    invoice_amount = to_float(invoice_amount)
    payment_amount = to_float(payment_amount)
    bank_amount = to_float(bank_amount)
    payment_fee = to_float(payment_fee)

    if payment_fee is None:
        payment_fee = 0.0

    metrics = {
        "invoice_amount": invoice_amount,
        "payment_amount": payment_amount,
        "bank_amount": bank_amount,
        "payment_fee": payment_fee,
        "outstanding_amount": None,
        "payment_coverage_percent": None,
        "bank_payment_difference": None,
        "invoice_payment_difference": None,
        "financial_status": "UNKNOWN"
    }

    # ---------------------------------------------------------
    # Invoice + Payment
    # ---------------------------------------------------------

    if invoice_amount is not None and payment_amount is not None:

        metrics["invoice_payment_difference"] = round(
            invoice_amount - payment_amount,
            2
        )

        if invoice_amount != 0:

            metrics["payment_coverage_percent"] = round(
                (payment_amount / invoice_amount) * 100,
                2
            )

        metrics["outstanding_amount"] = round(
            invoice_amount - payment_amount,
            2
        )

        if abs(invoice_amount - payment_amount) <= 0.01:

            metrics["outstanding_amount"] = 0.0
            metrics["payment_coverage_percent"] = 100.0
            metrics["financial_status"] = "FULLY_PAID"

        elif payment_amount < invoice_amount:

            metrics["financial_status"] = "PARTIALLY_PAID"

        elif payment_amount > invoice_amount:

            metrics["financial_status"] = "OVERPAID"

    # ---------------------------------------------------------
    # Bank + Payment
    # ---------------------------------------------------------

    if payment_amount is not None and bank_amount is not None:

        metrics["bank_payment_difference"] = round(
            bank_amount - payment_amount,
            2
        )

        if abs(bank_amount - payment_amount) > 0.01:

            metrics["financial_status"] = "BANK_MISMATCH"

    # ---------------------------------------------------------
    # Missing invoice
    # ---------------------------------------------------------

    if invoice_amount is None and payment_amount is not None:

        metrics["financial_status"] = "INCOMPLETE"

    # ---------------------------------------------------------
    # Missing payment
    # ---------------------------------------------------------

    if payment_amount is None and bank_amount is not None:

        metrics["financial_status"] = "INCOMPLETE"

    return metrics


# ============================================================
# INVESTIGATION FINDING
# ============================================================

def generate_investigation_finding(
    category,
    metrics
):
    """
    Generate a human-readable investigation finding.
    """

    invoice_amount = metrics.get("invoice_amount")
    payment_amount = metrics.get("payment_amount")
    bank_amount = metrics.get("bank_amount")
    outstanding = metrics.get("outstanding_amount")
    coverage = metrics.get("payment_coverage_percent")
    difference = metrics.get("bank_payment_difference")

    if category == "FULL_RECONCILIATION":

        return (
            "The invoice has been fully settled. "
            "The payment amount matches the invoice and "
            "the bank transaction confirms the payment."
        )

    if category == "FEE_ADJUSTED_RECONCILIATION":

        return (
            "The payment and bank transaction can be reconciled "
            "with the invoice after accounting for the applicable "
            "transaction fee."
        )

    if category == "PARTIAL_PAYMENT":

        return (
            f"The payment of {payment_amount:.2f} is confirmed by "
            f"the bank but covers only {coverage:.2f}% of the invoice. "
            f"An outstanding balance of {outstanding:.2f} remains."
        )

    if category == "OVERPAYMENT":

        overpayment = abs(outstanding) if outstanding is not None else 0.0

        return (
            f"The payment exceeds the invoice amount by "
            f"{overpayment:.2f}. The excess amount requires "
            f"financial review before final reconciliation."
        )

    if category == "BANK_PAYMENT_MISMATCH":

        return (
            f"The payment amount of {payment_amount:.2f} does not "
            f"match the bank amount of {bank_amount:.2f}. "
            f"The recorded difference is {difference:.2f}."
        )

    if category == "MISSING_PAYMENT":

        return (
            "An expected payment could not be matched to the "
            "available financial records. The available evidence "
            "is insufficient to confirm settlement."
        )

    if category == "MISSING_BANK_TRANSACTION":

        return (
            "A payment record exists, but the corresponding bank "
            "transaction could not be located. The payment therefore "
            "cannot be fully verified against bank records."
        )

    if category == "INCOMPLETE_RECONCILIATION":

        return (
            "Payment and bank information are available, but the "
            "corresponding invoice information is incomplete. "
            "Full reconciliation cannot be completed."
        )

    if category == "MULTI_INVOICE_PAYMENT":

        return (
            "A single payment is associated with multiple invoices. "
            "The payment cannot be treated as a simple one-to-one "
            "invoice reconciliation."
        )

    return (
        "The available financial evidence does not match a known "
        "reconciliation pattern. Manual investigation is required."
    )


# ============================================================
# LIKELY CAUSE
# ============================================================

def generate_likely_cause(
    category,
    metrics
):
    """
    Determine the most likely business explanation for the exception.
    """

    if category == "FULL_RECONCILIATION":

        return (
            "No financial exception identified. "
            "The transaction appears to be correctly reconciled."
        )

    if category == "FEE_ADJUSTED_RECONCILIATION":

        return (
            "The difference between the invoice and payment is "
            "explained by the recorded transaction fee."
        )

    if category == "PARTIAL_PAYMENT":

        coverage = metrics.get("payment_coverage_percent")

        if coverage is not None and coverage < 50:

            return (
                "Possible major partial settlement, missing subsequent "
                "payment, or customer underpayment."
            )

        return (
            "Possible partial settlement or an additional payment "
            "that has not yet been matched to the invoice."
        )

    if category == "OVERPAYMENT":

        return (
            "Possible duplicate payment, customer overpayment, "
            "incorrect payment allocation, or excess settlement."
        )

    if category == "BANK_PAYMENT_MISMATCH":

        return (
            "Possible bank processing difference, incorrect payment "
            "record, transaction adjustment, fee handling issue, "
            "or incorrect bank reconciliation."
        )

    if category == "MISSING_PAYMENT":

        return (
            "Possible payment processing delay, missing payment record, "
            "unmatched customer payment, or incomplete payment data."
        )

    if category == "MISSING_BANK_TRANSACTION":

        return (
            "Possible bank posting delay, missing bank statement entry, "
            "or payment that has not yet reached the bank account."
        )

    if category == "INCOMPLETE_RECONCILIATION":

        return (
            "The invoice information is missing or could not be matched "
            "to the payment and bank records."
        )

    if category == "MULTI_INVOICE_PAYMENT":

        return (
            "The customer appears to have settled multiple invoices "
            "through a single payment, requiring allocation of the "
            "payment across invoices."
        )

    return (
        "The root cause cannot be reliably determined from the "
        "available financial evidence."
    )


# ============================================================
# RECOMMENDED ACTION
# ============================================================

def generate_recommended_action(
    category,
    metrics
):
    """
    Generate the next operational action for an analyst.
    """

    if category == "FULL_RECONCILIATION":

        return (
            "Mark the transaction as reconciled and close the case."
        )

    if category == "FEE_ADJUSTED_RECONCILIATION":

        return (
            "Verify the transaction fee and mark the transaction "
            "as reconciled."
        )

    if category == "PARTIAL_PAYMENT":

        return (
            "Search for additional payments, verify the outstanding "
            "invoice balance, and confirm whether the customer still "
            "owes the remaining amount."
        )

    if category == "OVERPAYMENT":

        return (
            "Verify whether the excess amount resulted from a duplicate "
            "or incorrect payment and determine whether a refund or "
            "account adjustment is required."
        )

    if category == "BANK_PAYMENT_MISMATCH":

        return (
            "Compare the payment gateway record with the bank statement "
            "and investigate the amount difference before reconciliation."
        )

    if category == "MISSING_PAYMENT":

        return (
            "Search payment records and payment gateway information, "
            "then verify the customer's payment status."
        )

    if category == "MISSING_BANK_TRANSACTION":

        return (
            "Check the bank statement and posting history to determine "
            "whether the payment is delayed or genuinely missing."
        )

    if category == "INCOMPLETE_RECONCILIATION":

        return (
            "Retrieve the missing invoice information and establish "
            "the invoice-payment relationship before reconciliation."
        )

    if category == "MULTI_INVOICE_PAYMENT":

        return (
            "Review the referenced invoices and allocate the payment "
            "across them before completing reconciliation."
        )

    return (
        "Escalate the case for manual financial investigation."
    )


# ============================================================
# STRUCTURED REASONING
# ============================================================

def generate_reasoning_steps(
    category,
    metrics,
    invoice_id=None,
    payment_id=None,
    bank_id=None,
    related_invoice_ids=None
):
    """
    Generate structured investigation reasoning.

    These steps explain how TANGLE reached its conclusion.
    """

    steps = []

    invoice_amount = metrics.get("invoice_amount")
    payment_amount = metrics.get("payment_amount")
    bank_amount = metrics.get("bank_amount")
    outstanding = metrics.get("outstanding_amount")
    coverage = metrics.get("payment_coverage_percent")
    bank_difference = metrics.get("bank_payment_difference")
    payment_fee = metrics.get("payment_fee", 0.0)

    # ---------------------------------------------------------
    # FULL RECONCILIATION
    # ---------------------------------------------------------

    if category == "FULL_RECONCILIATION":

        steps.append(
            f"Invoice {invoice_id} was identified with amount "
            f"{invoice_amount:.2f}."
        )

        steps.append(
            f"Payment {payment_id} was identified with amount "
            f"{payment_amount:.2f}."
        )

        steps.append(
            f"Bank transaction {bank_id} confirms amount "
            f"{bank_amount:.2f}."
        )

        steps.append(
            "Invoice, payment and bank amounts match within "
            "the allowed tolerance."
        )

        steps.append(
            "No outstanding balance remains."
        )

    # ---------------------------------------------------------
    # FEE ADJUSTED
    # ---------------------------------------------------------

    elif category == "FEE_ADJUSTED_RECONCILIATION":

        steps.append(
            f"Invoice amount identified as {invoice_amount:.2f}."
        )

        steps.append(
            f"Payment amount identified as {payment_amount:.2f}."
        )

        steps.append(
            f"Recorded payment fee is {payment_fee:.2f}."
        )

        steps.append(
            f"Bank transaction confirms amount {bank_amount:.2f}."
        )

        steps.append(
            "The payment and invoice can be reconciled after "
            "accounting for the transaction fee."
        )

    # ---------------------------------------------------------
    # PARTIAL PAYMENT
    # ---------------------------------------------------------

    elif category == "PARTIAL_PAYMENT":

        steps.append(
            f"Invoice amount identified as {invoice_amount:.2f}."
        )

        steps.append(
            f"Payment of {payment_amount:.2f} was received."
        )

        steps.append(
            f"Bank transaction confirms {bank_amount:.2f}."
        )

        steps.append(
            f"Payment covers {coverage:.2f}% of the invoice."
        )

        steps.append(
            f"Outstanding balance is {outstanding:.2f}."
        )

        if coverage is not None and coverage < 50:

            steps.append(
                "Payment coverage is below 50%, indicating a "
                "significant unpaid invoice balance."
            )

        elif coverage is not None and coverage < 75:

            steps.append(
                "Payment coverage is below 75%, indicating a "
                "material outstanding balance."
            )

        else:

            steps.append(
                "The invoice has been partially settled but remains "
                "unpaid in full."
            )

        steps.append(
            "Additional payment records should be checked before "
            "final resolution."
        )

    # ---------------------------------------------------------
    # OVERPAYMENT
    # ---------------------------------------------------------

    elif category == "OVERPAYMENT":

        overpayment = (
            abs(outstanding)
            if outstanding is not None
            else 0.0
        )

        steps.append(
            f"Invoice amount identified as {invoice_amount:.2f}."
        )

        steps.append(
            f"Payment of {payment_amount:.2f} was received."
        )

        if bank_amount is not None:

            steps.append(
                f"Bank transaction confirms {bank_amount:.2f}."
            )

        steps.append(
            f"Payment exceeds the invoice by {overpayment:.2f}."
        )

        steps.append(
            "The excess amount requires financial review."
        )

    # ---------------------------------------------------------
    # BANK PAYMENT MISMATCH
    # ---------------------------------------------------------

    elif category == "BANK_PAYMENT_MISMATCH":

        steps.append(
            f"Payment amount identified as {payment_amount:.2f}."
        )

        steps.append(
            f"Bank transaction amount identified as "
            f"{bank_amount:.2f}."
        )

        steps.append(
            f"The bank-payment difference is "
            f"{bank_difference:.2f}."
        )

        steps.append(
            "The payment and bank records do not agree."
        )

        steps.append(
            "The discrepancy requires investigation before "
            "the transaction can be reconciled."
        )

    # ---------------------------------------------------------
    # MISSING PAYMENT
    # ---------------------------------------------------------

    elif category == "MISSING_PAYMENT":

        if invoice_id:

            steps.append(
                f"Invoice {invoice_id} was identified."
            )

        if bank_id and bank_amount is not None:

            steps.append(
                f"Bank transaction {bank_id} was identified "
                f"with amount {bank_amount:.2f}."
            )

        steps.append(
            "The expected payment record could not be matched."
        )

        steps.append(
            "Invoice-level payment coverage cannot be calculated "
            "because the payment amount is unavailable."
        )

        steps.append(
            "Payment records and gateway information should be "
            "checked for an unmatched transaction."
        )

    # ---------------------------------------------------------
    # MISSING BANK TRANSACTION
    # ---------------------------------------------------------

    elif category == "MISSING_BANK_TRANSACTION":

        if invoice_id:

            steps.append(
                f"Invoice {invoice_id} was identified."
            )

        steps.append(
            f"Payment {payment_id} was identified with amount "
            f"{payment_amount:.2f}."
        )

        steps.append(
            "The corresponding bank transaction could not be matched."
        )

        steps.append(
            "The payment cannot be fully verified against bank records."
        )

        steps.append(
            "The bank statement and posting history should be checked."
        )

    # ---------------------------------------------------------
    # INCOMPLETE RECONCILIATION
    # ---------------------------------------------------------

    elif category == "INCOMPLETE_RECONCILIATION":

        steps.append(
            f"Payment amount identified as {payment_amount:.2f}."
        )

        steps.append(
            f"Bank transaction amount identified as {bank_amount:.2f}."
        )

        steps.append(
            "The payment and bank records are available."
        )

        steps.append(
            "The corresponding invoice could not be verified."
        )

        steps.append(
            "The invoice must be retrieved before reconciliation."
        )

    # ---------------------------------------------------------
    # MULTI INVOICE
    # ---------------------------------------------------------

    elif category == "MULTI_INVOICE_PAYMENT":

        if related_invoice_ids:

            steps.append(
                f"Payment {payment_id} references multiple invoices: "
                f"{related_invoice_ids}."
            )

        steps.append(
            f"Payment amount identified as {payment_amount:.2f}."
        )

        if bank_amount is not None:

            steps.append(
                f"Bank transaction confirms {bank_amount:.2f}."
            )

        steps.append(
            "The payment cannot be evaluated as a single-invoice "
            "reconciliation."
        )

        steps.append(
            "The payment must be allocated across the referenced "
            "invoices."
        )

        steps.append(
            "Manual allocation review is recommended."
        )

    # ---------------------------------------------------------
    # UNKNOWN
    # ---------------------------------------------------------

    else:

        steps.append(
            "TANGLE could not establish a known reconciliation pattern."
        )

        steps.append(
            "Available financial evidence is insufficient "
            "for automatic reconciliation."
        )

        steps.append(
            "Manual financial review is required."
        )

    return steps


# ============================================================
# EVIDENCE SUMMARY
# ============================================================

def generate_evidence_summary(
    category,
    metrics
):
    """
    Generate a concise financial evidence summary.
    """

    invoice_amount = metrics.get("invoice_amount")
    payment_amount = metrics.get("payment_amount")
    bank_amount = metrics.get("bank_amount")
    payment_fee = metrics.get("payment_fee")
    outstanding = metrics.get("outstanding_amount")
    coverage = metrics.get("payment_coverage_percent")
    bank_difference = metrics.get("bank_payment_difference")
    financial_status = metrics.get("financial_status")

    evidence = []

    if invoice_amount is not None:

        evidence.append(
            f"Invoice amount: {invoice_amount:.2f}"
        )

    if payment_amount is not None:

        evidence.append(
            f"Payment amount: {payment_amount:.2f}"
        )

    if bank_amount is not None:

        evidence.append(
            f"Bank amount: {bank_amount:.2f}"
        )

    if payment_fee is not None and payment_fee != 0:

        evidence.append(
            f"Payment fee: {payment_fee:.2f}"
        )

    if outstanding is not None:

        evidence.append(
            f"Outstanding amount: {outstanding:.2f}"
        )

    if coverage is not None:

        evidence.append(
            f"Payment coverage: {coverage:.2f}%"
        )

    if bank_difference is not None:

        evidence.append(
            f"Bank-payment difference: {bank_difference:.2f}"
        )

    evidence.append(
        f"Financial status: {financial_status}"
    )

    return " | ".join(evidence)


# ============================================================
# FINANCIAL IMPACT
# ============================================================

def calculate_financial_impact(metrics):
    """
    Determine the financial impact of the case.
    """

    outstanding = metrics.get("outstanding_amount")

    if outstanding is None:

        return "FINANCIAL_IMPACT_UNDETERMINED"

    if outstanding > 0:

        return (
            f"OUTSTANDING_BALANCE_{outstanding:.2f}"
        )

    if outstanding < 0:

        return (
            f"OVERPAYMENT_{abs(outstanding):.2f}"
        )

    return "NO_OUTSTANDING_BALANCE"


# ============================================================
# MAIN INVESTIGATION FUNCTION
# ============================================================

def investigate(case):
    """
    Investigate a detected financial case.

    Produces:
    - hypothesis
    - confidence
    - category
    - rationale
    - investigation finding
    - likely cause
    - suggested action
    - financial metrics
    - reasoning steps
    - evidence summary
    - financial impact
    - risk assessment
    """

    if case is None:
        case = {}

    record_id = case.get("record_id")

    invoice_amount = to_float(
        case.get("invoice_amount")
    )

    payment_amount = to_float(
        case.get("payment_amount")
    )

    payment_fee = to_float(
        case.get("payment_fee")
    )

    bank_amount = to_float(
        case.get("bank_amount")
    )

    invoice_id = case.get("invoice_id")

    payment_id = case.get("payment_id")

    bank_id = case.get(
        "bank_transaction_id"
    )

    gateway_reference = case.get(
        "gateway_reference"
    )

    category = case.get(
        "category",
        "UNKNOWN"
    )

    detection_confidence = case.get(
        "confidence",
        0.0
    )

    # ---------------------------------------------------------
    # Financial metrics
    # ---------------------------------------------------------

    metrics = calculate_financial_metrics(
        invoice_amount=invoice_amount,
        payment_amount=payment_amount,
        bank_amount=bank_amount,
        payment_fee=payment_fee
    )

    # ---------------------------------------------------------
    # Investigation logic
    # ---------------------------------------------------------

    if category == "FULL_RECONCILIATION":

        hypothesis = (
            "Invoice, payment and bank amounts are fully reconciled."
        )

        rationale = (
            f"Invoice = {invoice_amount}, "
            f"payment = {payment_amount}, "
            f"bank = {bank_amount}."
        )

        suggested_action = (
            "Mark the transaction as reconciled."
        )

    elif category == "FEE_ADJUSTED_RECONCILIATION":

        hypothesis = (
            "The payment and bank transaction reconcile with "
            "the invoice after accounting for the transaction fee."
        )

        rationale = (
            f"Invoice = {invoice_amount}, "
            f"payment = {payment_amount}, "
            f"fee = {payment_fee}, "
            f"bank = {bank_amount}."
        )

        suggested_action = (
            "Record the transaction fee and mark the "
            "transaction as reconciled."
        )

    elif category == "PARTIAL_PAYMENT":

        outstanding = metrics["outstanding_amount"]
        coverage = metrics["payment_coverage_percent"]

        hypothesis = (
            "The bank transaction matches the payment, "
            "but the payment does not fully reconcile against "
            "the invoice."
        )

        rationale = (
            f"Invoice = {invoice_amount}, "
            f"payment = {payment_amount}, "
            f"bank = {bank_amount}, "
            f"fee = {payment_fee}, "
            f"outstanding amount = {outstanding}, "
            f"payment coverage = {coverage}%."
        )

        suggested_action = (
            "Investigate the outstanding invoice balance "
            "and verify whether an additional payment is due."
        )

    elif category == "OVERPAYMENT":

        overpayment = abs(
            metrics["outstanding_amount"]
        )

        hypothesis = (
            "The payment exceeds the invoice amount."
        )

        rationale = (
            f"Invoice = {invoice_amount}, "
            f"payment = {payment_amount}, "
            f"bank = {bank_amount}, "
            f"overpayment amount = {overpayment}."
        )

        suggested_action = (
            "Review the overpayment and determine whether "
            "a refund or account adjustment is required."
        )

    elif category == "BANK_PAYMENT_MISMATCH":

        difference = metrics[
            "bank_payment_difference"
        ]

        hypothesis = (
            "The bank transaction amount does not match "
            "the payment amount."
        )

        rationale = (
            f"Payment = {payment_amount}, "
            f"bank = {bank_amount}, "
            f"bank-payment difference = {difference}."
        )

        suggested_action = (
            "Investigate the payment and bank transaction "
            "discrepancy."
        )

    elif category == "MISSING_PAYMENT":

        hypothesis = (
            "An expected payment could not be matched "
            "to the available financial records."
        )

        if bank_amount is not None:

            rationale = (
                f"Bank transaction {bank_id} contains amount "
                f"{bank_amount}, but the expected payment "
                f"record was not available."
            )

        else:

            rationale = (
                f"Invoice {invoice_id} exists, but the "
                f"expected payment could not be located."
            )

        suggested_action = (
            "Search payment records and verify the "
            "customer's payment status."
        )

    elif category == "MISSING_BANK_TRANSACTION":

        hypothesis = (
            "A payment exists but the corresponding "
            "bank transaction could not be matched."
        )

        rationale = (
            f"Payment {payment_id} contains amount "
            f"{payment_amount}, but the corresponding "
            f"bank transaction was not found."
        )

        suggested_action = (
            "Verify the bank statement and investigate "
            "the missing deposit."
        )

    elif category == "INCOMPLETE_RECONCILIATION":

        hypothesis = (
            "The bank transaction matches the payment, "
            "but the invoice could not be verified."
        )

        rationale = (
            f"Payment = {payment_amount}, "
            f"bank = {bank_amount}, "
            f"but invoice amount is unavailable."
        )

        suggested_action = (
            "Retrieve the related invoice before reconciliation."
        )

    elif category == "MULTI_INVOICE_PAYMENT":

        related_invoice_ids = case.get(
            "related_invoice_ids",
            ""
        )

        related_invoice_count = case.get(
            "related_invoice_count",
            0
        )

        hypothesis = (
            "A single payment references multiple invoices "
            "and requires allocation review."
        )

        rationale = (
            f"Payment {payment_id} references "
            f"{related_invoice_count} invoices: "
            f"{related_invoice_ids}. "
            f"Payment amount = {payment_amount}, "
            f"bank amount = {bank_amount}."
        )

        suggested_action = (
            "Review payment allocation across the "
            "referenced invoices before reconciliation."
        )

        metrics["financial_status"] = "MULTI_INVOICE"

    else:

        hypothesis = (
            "The financial records do not match a known "
            "reconciliation pattern."
        )

        rationale = (
            f"Unable to determine a reliable financial "
            f"relationship for record {record_id}."
        )

        suggested_action = (
            "Escalate the case for manual financial review."
        )

    # ---------------------------------------------------------
    # Investigation intelligence
    # ---------------------------------------------------------

    investigation_finding = generate_investigation_finding(
        category=category,
        metrics=metrics
    )

    likely_cause = generate_likely_cause(
        category=category,
        metrics=metrics
    )

    recommended_action = generate_recommended_action(
        category=category,
        metrics=metrics
    )

    # ---------------------------------------------------------
    # Structured reasoning
    # ---------------------------------------------------------

    reasoning_steps = generate_reasoning_steps(
        category=category,
        metrics=metrics,
        invoice_id=invoice_id,
        payment_id=payment_id,
        bank_id=bank_id,
        related_invoice_ids=case.get(
            "related_invoice_ids"
        )
    )

    evidence_summary = generate_evidence_summary(
        category=category,
        metrics=metrics
    )

    financial_impact = calculate_financial_impact(
        metrics
    )

    # ---------------------------------------------------------
    # Risk Engine
    # ---------------------------------------------------------

    risk_input = {
        "category": category,

        "invoice_amount": metrics.get(
            "invoice_amount"
        ),

        "payment_amount": metrics.get(
            "payment_amount"
        ),

        "bank_amount": metrics.get(
            "bank_amount"
        ),

        "outstanding_amount": metrics.get(
            "outstanding_amount"
        ),

        "payment_coverage_percent": metrics.get(
            "payment_coverage_percent"
        ),

        "financial_status": metrics.get(
            "financial_status"
        ),

        "confidence": detection_confidence
    }

    risk_result = calculate_risk(
        risk_input
    )

    # ---------------------------------------------------------
    # Final investigation result
    # ---------------------------------------------------------

    result = {

        # Core investigation
        "hypothesis": hypothesis,

        "confidence": detection_confidence,

        "category": category,

        "rationale": rationale,

        "suggested_action": suggested_action,

        # New investigation intelligence
        "investigation_finding": investigation_finding,

        "likely_cause": likely_cause,

        "recommended_action": recommended_action,

        # Financial metrics
        "financial_metrics": metrics,

        # Structured reasoning
        "reasoning_steps": reasoning_steps,

        "evidence_summary": evidence_summary,

        "financial_impact": financial_impact,

        # Risk assessment
        "risk_level": risk_result[
            "risk_level"
        ],

        "priority_score": risk_result[
            "priority_score"
        ],

        "human_review_required": risk_result[
            "human_review_required"
        ],

        "risk_reason": risk_result[
            "risk_reason"
        ]
    }

    return result


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("TANGLE INVESTIGATION AGENT TEST")
    print("=" * 70)

    test_case = {

        "record_type": "PAYMENT",

        "record_id": "PAY-TEST-001",

        "invoice_id": "INV-TEST-001",

        "invoice_amount": 1500.0,

        "payment_id": "PAY-TEST-001",

        "payment_amount": 807.80,

        "payment_fee": 0.0,

        "bank_transaction_id": "BANK-TEST-001",

        "bank_amount": 807.80,

        "gateway_reference": "PAY-TEST-001",

        "category": "PARTIAL_PAYMENT",

        "confidence": 0.97
    }

    result = investigate(
        test_case
    )

    print()

    print(
        json.dumps(
            result,
            indent=4
        )
    )

    print()

    print("=" * 70)
    print("INVESTIGATION AGENT TEST COMPLETE")
    print("=" * 70)