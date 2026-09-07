
import os
import json
import pandas as pd

from agents.exception_detector import detect_exception
from agents.agent import investigate
from agents.decision_engine import make_decision


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

INVOICE_FILE = os.path.join(
    DATA_DIR,
    "invoices.csv"
)

PAYMENT_FILE = os.path.join(
    DATA_DIR,
    "payments.csv"
)

BANK_FILE = os.path.join(
    DATA_DIR,
    "bank_transactions.csv"
)

OUTPUT_FILE = os.path.join(
    DATA_DIR,
    "agent_results.csv"
)


# ============================================================
# DATA LOADING
# ============================================================

def load_invoices():

    return pd.read_csv(
        INVOICE_FILE
    )


def load_payments():

    return pd.read_csv(
        PAYMENT_FILE
    )


def load_bank_transactions():

    return pd.read_csv(
        BANK_FILE
    )


# ============================================================
# VALUE CLEANING
# ============================================================

def clean_value(value):
    """
    Convert pandas NaN values into None.
    Keep all other values unchanged.
    """

    if pd.isna(value):

        return None

    return value


# ============================================================
# REFERENCE HANDLING
# ============================================================

def split_references(reference):
    """
    Split multi-invoice references.

    Example:

    INV-0001|INV-0002|INV-0003

    becomes:

    [
        "INV-0001",
        "INV-0002",
        "INV-0003"
    ]
    """

    if reference is None:

        return []

    if pd.isna(reference):

        return []

    reference = str(
        reference
    ).strip()

    if not reference:

        return []

    return [
        item.strip()
        for item in reference.split("|")
        if item.strip()
    ]


# ============================================================
# INVOICE LOOKUPS
# ============================================================

def find_payments_for_invoice(
    payments,
    invoice_id
):
    """
    Find all payments referencing an invoice.
    """

    if invoice_id is None:

        return []

    matches = []

    for _, payment in payments.iterrows():

        references = split_references(
            payment.get(
                "invoice_reference"
            )
        )

        if invoice_id in references:

            matches.append(
                payment
            )

    return matches


def find_payment_for_invoice(
    payments,
    invoice_id
):
    """
    Find the first payment referencing an invoice.
    """

    matches = find_payments_for_invoice(
        payments,
        invoice_id
    )

    if matches:

        return matches[0]

    return None


# ============================================================
# PAYMENT LOOKUPS
# ============================================================

def find_invoices_for_payment(
    invoices,
    payment
):
    """
    Find all invoices referenced by a payment.
    """

    if payment is None:

        return []

    references = split_references(
        payment.get(
            "invoice_reference"
        )
    )

    matches = []

    for invoice_id in references:

        invoice_match = invoices[
            invoices["invoice_id"].astype(str)
            == str(invoice_id)
        ]

        if not invoice_match.empty:

            matches.append(
                invoice_match.iloc[0]
            )

    return matches


def find_invoice_for_payment(
    invoices,
    payment
):
    """
    Find the first invoice referenced by a payment.
    """

    matches = find_invoices_for_payment(
        invoices,
        payment
    )

    if matches:

        return matches[0]

    return None


# ============================================================
# BANK LOOKUPS
# ============================================================

def find_banks_for_payment(
    banks,
    payment
):
    """
    Find bank transactions associated with a payment.
    """

    if payment is None:

        return []

    payment_id = payment.get(
        "payment_id"
    )

    gateway_reference = payment.get(
        "gateway_reference"
    )

    matches = []

    for _, bank in banks.iterrows():

        bank_reference = bank.get(
            "gateway_reference"
        )

        bank_payment_id = bank.get(
            "payment_id"
        )

        if (
            payment_id is not None
            and bank_payment_id is not None
            and str(bank_payment_id)
            == str(payment_id)
        ):

            matches.append(
                bank
            )

        elif (
            gateway_reference is not None
            and bank_reference is not None
            and str(bank_reference)
            == str(gateway_reference)
        ):

            matches.append(
                bank
            )

    return matches


def find_bank_for_payment(
    banks,
    payment
):
    """
    Find the first bank transaction associated with a payment.
    """

    matches = find_banks_for_payment(
        banks,
        payment
    )

    if matches:

        return matches[0]

    return None


# ============================================================
# BANK -> PAYMENT LOOKUPS
# ============================================================

def find_payments_for_bank(
    payments,
    bank
):
    """
    Find payments associated with a bank transaction.
    """

    if bank is None:

        return []

    bank_reference = bank.get(
        "gateway_reference"
    )

    bank_payment_id = bank.get(
        "payment_id"
    )

    matches = []

    for _, payment in payments.iterrows():

        payment_id = payment.get(
            "payment_id"
        )

        payment_gateway_reference = payment.get(
            "gateway_reference"
        )

        if (
            bank_payment_id is not None
            and payment_id is not None
            and str(bank_payment_id)
            == str(payment_id)
        ):

            matches.append(
                payment
            )

        elif (
            bank_reference is not None
            and payment_gateway_reference is not None
            and str(bank_reference)
            == str(payment_gateway_reference)
        ):

            matches.append(
                payment
            )

    return matches


def find_payment_for_bank(
    payments,
    bank
):
    """
    Find the first payment associated with a bank transaction.
    """

    matches = find_payments_for_bank(
        payments,
        bank
    )

    if matches:

        return matches[0]

    return None


# ============================================================
# CASE BUILDING
# ============================================================

def build_case(
    record_type,
    record,
    invoice=None,
    payment=None,
    bank=None,
    category=None,
    confidence=None,
    suggested_action=None
):
    """
    Build the investigation case passed to the
    investigation agent.
    """

    case = {

        "record_type":
            record_type,

        "record_id":
            clean_value(
                record.get(
                    "invoice_id"
                    if record_type == "INVOICE"
                    else
                    "payment_id"
                    if record_type == "PAYMENT"
                    else
                    "bank_transaction_id"
                )
            )
    }

    # --------------------------------------------------------
    # INVOICE DATA
    # --------------------------------------------------------

    if invoice is not None:

        case["invoice_id"] = clean_value(
            invoice.get(
                "invoice_id"
            )
        )

        case["invoice_customer"] = clean_value(
            invoice.get(
                "customer"
            )
        )

        case["invoice_date"] = clean_value(
            invoice.get(
                "invoice_date"
            )
        )

        case["due_date"] = clean_value(
            invoice.get(
                "due_date"
            )
        )

        case["invoice_amount"] = clean_value(
            invoice.get(
                "amount"
            )
        )

        case["invoice_currency"] = clean_value(
            invoice.get(
                "currency"
            )
        )

    # --------------------------------------------------------
    # PAYMENT DATA
    # --------------------------------------------------------

    if payment is not None:

        case["payment_id"] = clean_value(
            payment.get(
                "payment_id"
            )
        )

        case["payment_invoice_reference"] = clean_value(
            payment.get(
                "invoice_reference"
            )
        )

        case["payment_customer"] = clean_value(
            payment.get(
                "customer"
            )
        )

        case["payment_date"] = clean_value(
            payment.get(
                "payment_date"
            )
        )

        case["payment_amount"] = clean_value(
            payment.get(
                "amount"
            )
        )

        case["payment_currency"] = clean_value(
            payment.get(
                "currency"
            )
        )

        case["payment_fee"] = clean_value(
            payment.get(
                "fee",
                0.0
            )
        )

        case["original_invoice_amount"] = clean_value(
            payment.get(
                "original_invoice_amount"
            )
        )

        case["gateway_reference"] = clean_value(
            payment.get(
                "gateway_reference"
            )
        )

    # --------------------------------------------------------
    # MULTI-INVOICE PAYMENT
    # --------------------------------------------------------

    if payment is not None:

        references = split_references(
            payment.get(
                "invoice_reference"
            )
        )

        if len(references) > 1:

            case["related_invoice_count"] = len(
                references
            )

            case["related_invoice_ids"] = "|".join(
                references
            )

            case["record_id"] = clean_value(
                payment.get(
                    "payment_id"
                )
            )

    # --------------------------------------------------------
    # BANK DATA
    # --------------------------------------------------------

    if bank is not None:

        case["bank_transaction_id"] = clean_value(
            bank.get(
                "bank_transaction_id"
            )
        )

        case["bank_deposit_date"] = clean_value(
            bank.get(
                "deposit_date"
            )
        )

        case["bank_amount"] = clean_value(
            bank.get(
                "amount"
            )
        )

        case["bank_currency"] = clean_value(
            bank.get(
                "currency"
            )
        )

        if case.get(
            "gateway_reference"
        ) is None:

            case["gateway_reference"] = clean_value(
                bank.get(
                    "gateway_reference"
                )
            )

    # --------------------------------------------------------
    # CASE CLASSIFICATION
    # --------------------------------------------------------

    case["category"] = category

    case["confidence"] = confidence

    case["suggested_action"] = suggested_action

    return case


# ============================================================
# CASE DISPLAY
# ============================================================

def print_case_data(case):
    """
    Print the raw investigation data.
    """

    print()

    print(
        "Investigation data:"
    )

    print(
        json.dumps(
            case,
            indent=4,
            default=str
        )
    )


# ============================================================
# CASE ID
# ============================================================

def get_case_key(case):
    """
    Create a stable unique key for a financial chain.
    """

    invoice_id = case.get(
        "invoice_id"
    )

    payment_id = case.get(
        "payment_id"
    )

    bank_id = case.get(
        "bank_transaction_id"
    )

    return (
        f"INV:{invoice_id}"
        f"|PAY:{payment_id}"
        f"|BANK:{bank_id}"
    )


def generate_case_id(
    case_number
):
    """
    Generate stable sequential case IDs.
    """

    return (
        f"CASE-{case_number:04d}"
    )


# ============================================================
# INVESTIGATION + DECISION + RESULT BUILDING
# ============================================================

def process_case(
    case
):
    """
    Run the investigation agent and decision engine.

    Converts the investigation result into the
    final flat CSV-compatible result.
    """

    investigation = investigate(
        case
    )

    print()

    print(
        "Investigation agent decision:"
    )

    print(
        json.dumps(
            investigation,
            indent=4,
            default=str
        )
    )

    decision = make_decision(
        investigation
    )

    print()

    print(
        "Business decision:"
    )

    print(
        json.dumps(
            decision,
            indent=4,
            default=str
        )
    )

    metrics = investigation.get(
        "financial_metrics",
        {}
    )

    # --------------------------------------------------------
    # STRUCTURED INVESTIGATION OUTPUT
    # --------------------------------------------------------

    reasoning_steps = investigation.get(
        "reasoning_steps",
        []
    )

    evidence_summary = investigation.get(
        "evidence_summary"
    )

    financial_impact = investigation.get(
        "financial_impact"
    )

    investigation_finding = investigation.get(
        "investigation_finding"
    )

    likely_cause = investigation.get(
        "likely_cause"
    )

    recommended_action = investigation.get(
        "recommended_action"
    )

    # --------------------------------------------------------
    # RISK ASSESSMENT
    # --------------------------------------------------------

    risk_level = investigation.get(
        "risk_level"
    )

    priority_score = investigation.get(
        "priority_score"
    )

    human_review_required = investigation.get(
        "human_review_required"
    )

    risk_reason = investigation.get(
        "risk_reason"
    )

    # --------------------------------------------------------
    # FLATTEN RESULT
    # --------------------------------------------------------

    result = {

        **case,

        # ----------------------------------------------------
        # Investigation
        # ----------------------------------------------------

        "hypothesis":
            investigation.get(
                "hypothesis"
            ),

        "investigation_confidence":
            investigation.get(
                "confidence"
            ),

        "rationale":
            investigation.get(
                "rationale"
            ),

        "investigation_action":
            investigation.get(
                "suggested_action"
            ),

        # ----------------------------------------------------
        # NEW STEP 6A
        # Investigation explanation
        # ----------------------------------------------------

        "investigation_finding":
            investigation_finding,

        "likely_cause":
            likely_cause,

        "recommended_action":
            recommended_action,

        # ----------------------------------------------------
        # Financial metrics
        # ----------------------------------------------------

        "invoice_amount":
            metrics.get(
                "invoice_amount"
            ),

        "payment_amount":
            metrics.get(
                "payment_amount"
            ),

        "bank_amount":
            metrics.get(
                "bank_amount"
            ),

        "payment_fee":
            metrics.get(
                "payment_fee"
            ),

        "outstanding_amount":
            metrics.get(
                "outstanding_amount"
            ),

        "payment_coverage_percent":
            metrics.get(
                "payment_coverage_percent"
            ),

        "bank_payment_difference":
            metrics.get(
                "bank_payment_difference"
            ),

        "invoice_payment_difference":
            metrics.get(
                "invoice_payment_difference"
            ),

        "financial_status":
            metrics.get(
                "financial_status"
            ),

        # ----------------------------------------------------
        # Business decision
        # ----------------------------------------------------

        "decision":
            decision.get(
                "decision"
            ),

        "reason":
            decision.get(
                "reason"
            ),

        "next_action":
            decision.get(
                "next_action"
            ),

        "decision_confidence":
            decision.get(
                "confidence"
            ),

        # ----------------------------------------------------
        # STRUCTURED REASONING
        # ----------------------------------------------------

        "reasoning_steps":
            json.dumps(
                reasoning_steps
            ),

        "evidence_summary":
            evidence_summary,

        "financial_impact":
            financial_impact,

        # ----------------------------------------------------
        # RISK ASSESSMENT
        # ----------------------------------------------------

        "risk_level":
            risk_level,

        "priority_score":
            priority_score,

        "human_review_required":
            human_review_required,

        "risk_reason":
            risk_reason
    }

    return result


# ============================================================
# CASE LOGGING
# ============================================================

def print_case_header(
    case
):
    """
    Print a compact case header.
    """

    print()

    print(
        f"\nInvestigating case "
        f"{case.get('case_number', '')}"
    )

    print(
        f"Case ID: "
        f"{case.get('case_id')}"
    )

    print(
        f"Record Type: "
        f"{case.get('record_type')}"
    )

    print(
        f"Record ID: "
        f"{case.get('record_id')}"
    )

    print(
        f"Detected Exception: "
        f"{case.get('category')}"
    )

    print(
        f"Detection Confidence: "
        f"{case.get('confidence')}"
    )


# ============================================================
# MAIN AGENT PIPELINE
# ============================================================

def run_agent():

    print(
        "=" * 60
    )

    print(
        "TANGLE AGENT INVESTIGATION SYSTEM"
    )

    print(
        "=" * 60
    )

    # --------------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------------

    invoices = load_invoices()

    payments = load_payments()

    banks = load_bank_transactions()

    print()

    print(
        "Loaded financial data:"
    )

    print(
        f"Invoices: {len(invoices)}"
    )

    print(
        f"Payments: {len(payments)}"
    )

    print(
        f"Bank transactions: {len(banks)}"
    )

    # --------------------------------------------------------
    # RESULT STORAGE
    # --------------------------------------------------------

    results = []

    processed_chain_keys = set()

    case_number = 1

    # ========================================================
    # 1. PROCESS INVOICES
    # ========================================================

    for _, invoice in invoices.iterrows():

        invoice_id = clean_value(
            invoice.get(
                "invoice_id"
            )
        )

        payments_for_invoice = (
            find_payments_for_invoice(
                payments,
                invoice_id
            )
        )

        if not payments_for_invoice:

            detection = detect_exception(
                invoice=invoice.to_dict(),
                payment=None,
                bank=None
            )

            case = build_case(
                record_type="INVOICE",
                record=invoice,
                invoice=invoice,
                category=detection["category"],
                confidence=detection["confidence"],
                suggested_action=detection[
                    "suggested_action"
                ]
            )

            case_key = get_case_key(
                case
            )

            if case_key in processed_chain_keys:

                continue

            processed_chain_keys.add(
                case_key
            )

            case["case_id"] = generate_case_id(
                case_number
            )

            case["case_number"] = case_number

            case_number += 1

            print_case_header(
                case
            )

            print_case_data(
                case
            )

            result = process_case(
                case
            )

            results.append(
                result
            )

    # ========================================================
    # 2. PROCESS PAYMENTS
    # ========================================================

    for _, payment in payments.iterrows():

        payment_id = clean_value(
            payment.get(
                "payment_id"
            )
        )

        invoices_for_payment = (
            find_invoices_for_payment(
                invoices,
                payment
            )
        )

        bank = find_bank_for_payment(
            banks,
            payment
        )

        references = split_references(
            payment.get(
                "invoice_reference"
            )
        )

        # ----------------------------------------------------
        # MULTI-INVOICE PAYMENT
        # ----------------------------------------------------

        if len(references) > 1:

            detection = detect_exception(
                invoice=None,
                payment=payment.to_dict(),
                bank=(
                    bank.to_dict()
                    if bank is not None
                    else None
                )
            )

            detection["category"] = (
                "MULTI_INVOICE_PAYMENT"
            )

            detection["confidence"] = 0.95

            detection["suggested_action"] = (
                "INVESTIGATE"
            )

            case = build_case(
                record_type="PAYMENT",
                record=payment,
                invoice=None,
                payment=payment,
                bank=bank,
                category=detection["category"],
                confidence=detection["confidence"],
                suggested_action=detection[
                    "suggested_action"
                ]
            )

            case_key = get_case_key(
                case
            )

            if case_key in processed_chain_keys:

                continue

            processed_chain_keys.add(
                case_key
            )

            case["case_id"] = generate_case_id(
                case_number
            )

            case["case_number"] = case_number

            case_number += 1

            print_case_header(
                case
            )

            print_case_data(
                case
            )

            result = process_case(
                case
            )

            results.append(
                result
            )

            continue

        # ----------------------------------------------------
        # NORMAL PAYMENT
        # ----------------------------------------------------

        invoice = None

        if invoices_for_payment:

            invoice = invoices_for_payment[0]

        detection = detect_exception(
            invoice=(
                invoice.to_dict()
                if invoice is not None
                else None
            ),
            payment=payment.to_dict(),
            bank=(
                bank.to_dict()
                if bank is not None
                else None
            )
        )

        case = build_case(
            record_type="PAYMENT",
            record=payment,
            invoice=invoice,
            payment=payment,
            bank=bank,
            category=detection["category"],
            confidence=detection["confidence"],
            suggested_action=detection[
                "suggested_action"
            ]
        )

        case_key = get_case_key(
            case
        )

        if case_key in processed_chain_keys:

            continue

        processed_chain_keys.add(
            case_key
        )

        case["case_id"] = generate_case_id(
            case_number
        )

        case["case_number"] = case_number

        case_number += 1

        print_case_header(
            case
        )

        print_case_data(
            case
        )

        result = process_case(
            case
        )

        results.append(
            result
        )

    # ========================================================
    # 3. PROCESS BANK TRANSACTIONS
    # ========================================================

    for _, bank in banks.iterrows():

        payment_matches = (
            find_payments_for_bank(
                payments,
                bank
            )
        )

        if payment_matches:

            continue

        detection = detect_exception(
            invoice=None,
            payment=None,
            bank=bank.to_dict()
        )

        case = build_case(
            record_type="BANK",
            record=bank,
            invoice=None,
            payment=None,
            bank=bank,
            category=detection["category"],
            confidence=detection["confidence"],
            suggested_action=detection[
                "suggested_action"
            ]
        )

        case_key = get_case_key(
            case
        )

        if case_key in processed_chain_keys:

            continue

        processed_chain_keys.add(
            case_key
        )

        case["case_id"] = generate_case_id(
            case_number
        )

        case["case_number"] = case_number

        case_number += 1

        print_case_header(
            case
        )

        print_case_data(
            case
        )

        result = process_case(
            case
        )

        results.append(
            result
        )

    # ========================================================
    # SAVE RESULTS
    # ========================================================

    results_df = pd.DataFrame(
        results
    )

    # Remove internal logging column.
    if "case_number" in results_df.columns:

        results_df = results_df.drop(
            columns=["case_number"]
        )

    results_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    print()

    print(
        "=" * 60
    )

    print(
        "AGENT INVESTIGATION COMPLETE"
    )

    print(
        "=" * 60
    )

    print()

    print(
        f"Detected cases processed: "
        f"{len(results_df)}"
    )

    if not results_df.empty:

        first_case = results_df.iloc[0][
            "case_id"
        ]

        last_case = results_df.iloc[-1][
            "case_id"
        ]

        print()

        print(
            "Case IDs generated:"
        )

        print(
            f"{first_case} to {last_case}"
        )

        print()

        print(
            "Category breakdown:"
        )

        print(
            results_df[
                "category"
            ].value_counts()
        )

        print()

        print(
            "Business decision breakdown:"
        )

        print(
            results_df[
                "decision"
            ].value_counts()
        )

        # ----------------------------------------------------
        # FINANCIAL METRIC SUMMARY
        # ----------------------------------------------------

        print()

        print(
            "Financial metrics summary:"
        )

        if "outstanding_amount" in results_df:

            outstanding = pd.to_numeric(
                results_df[
                    "outstanding_amount"
                ],
                errors="coerce"
            )

            coverage = pd.to_numeric(
                results_df[
                    "payment_coverage_percent"
                ],
                errors="coerce"
            )

            print(
                f"Total outstanding amount: "
                f"{outstanding.sum():.2f}"
            )

            print(
                f"Average payment coverage: "
                f"{coverage.mean():.2f}%"
            )

            print(
                f"Cases with outstanding balance: "
                f"{outstanding.gt(0).sum()}"
            )

        # ----------------------------------------------------
        # RISK SUMMARY
        # ----------------------------------------------------

        if "risk_level" in results_df:

            print()

            print(
                "Risk level breakdown:"
            )

            print(
                results_df[
                    "risk_level"
                ].value_counts()
            )

        if "human_review_required" in results_df:

            review_count = (
                results_df[
                    "human_review_required"
                ]
                .astype(str)
                .str.lower()
                .eq("true")
                .sum()
            )

            print()

            print(
                f"Cases requiring human review: "
                f"{review_count}"
            )

        if "priority_score" in results_df:

            priority = pd.to_numeric(
                results_df[
                    "priority_score"
                ],
                errors="coerce"
            )

            print(
                f"Average priority score: "
                f"{priority.mean():.2f}"
            )

            print(
                f"Highest priority score: "
                f"{priority.max():.0f}"
            )

        # ----------------------------------------------------
        # STRUCTURED INVESTIGATION SUMMARY
        # ----------------------------------------------------

        if "reasoning_steps" in results_df:

            print()

            print(
                "Structured AI reasoning: ENABLED"
            )

        if "evidence_summary" in results_df:

            print(
                "Evidence summaries: ENABLED"
            )

        if "financial_impact" in results_df:

            print(
                "Financial impact analysis: ENABLED"
            )

        if "investigation_finding" in results_df:

            print(
                "Investigation findings: ENABLED"
            )

        if "likely_cause" in results_df:

            print(
                "Likely cause analysis: ENABLED"
            )

        if "recommended_action" in results_df:

            print(
                "Recommended actions: ENABLED"
            )

        print()

        print(
            "Saved to:"
        )

        print(
            OUTPUT_FILE
        )

    print()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    run_agent()
