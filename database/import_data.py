from pathlib import Path
from datetime import datetime

import pandas as pd
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


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


INVOICES_FILE = DATA_DIR / "invoices.csv"
PAYMENTS_FILE = DATA_DIR / "payments.csv"
BANK_TRANSACTIONS_FILE = DATA_DIR / "bank_transactions.csv"
AGENT_RESULTS_FILE = DATA_DIR / "agent_results.csv"
REVIEW_QUEUE_FILE = DATA_DIR / "review_queue.csv"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_text(value):
    """
    Convert a value into a clean string.

    Blank values become None.
    """
    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except Exception:
        pass

    value = str(value).strip()

    if value == "":
        return None

    return value


def clean_float(value):
    """
    Convert a value to float.

    Invalid or blank values become None.
    """
    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except Exception:
        pass

    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def clean_int(value):
    """
    Convert a value to integer.

    Invalid or blank values become None.
    """
    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except Exception:
        pass

    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def clean_bool(value):
    """
    Convert common CSV boolean values into Python bool.
    """
    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except Exception:
        pass

    value = str(value).strip().upper()

    if value in {"TRUE", "1", "YES", "Y"}:
        return True

    if value in {"FALSE", "0", "NO", "N"}:
        return False

    return None


def clean_date(value):
    """
    Convert a CSV date into a Python date object.
    """
    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except Exception:
        pass

    try:
        return pd.to_datetime(value).date()
    except Exception:
        return None


def clean_datetime(value):
    """
    Convert a CSV datetime into a Python datetime object.
    """
    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except Exception:
        pass

    try:
        return pd.to_datetime(value).to_pydatetime()
    except Exception:
        return None


def read_csv_file(file_path):
    """
    Read a CSV file safely.
    """
    if not file_path.exists():
        print(f"[SKIP] File not found: {file_path}")
        return pd.DataFrame()

    print(f"[READ] {file_path}")

    try:
        df = pd.read_csv(file_path)

        print(
            f"       Loaded {len(df)} rows "
            f"and {len(df.columns)} columns."
        )

        return df

    except Exception as error:
        print(
            f"[ERROR] Could not read {file_path}: "
            f"{error}"
        )

        return pd.DataFrame()


# ============================================================
# INVOICE IMPORT
# ============================================================

def import_invoices(session):
    """
    Import invoices.csv into the invoices table.

    Existing invoice IDs are updated instead of duplicated.
    """

    df = read_csv_file(INVOICES_FILE)

    if df.empty:
        return {
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
        }

    inserted = 0
    updated = 0
    skipped = 0

    for _, row in df.iterrows():

        invoice_id = clean_text(
            row.get("invoice_id")
        )

        if not invoice_id:
            skipped += 1
            continue

        invoice = session.get(
            Invoice,
            invoice_id,
        )

        if invoice is None:

            invoice = Invoice(
                invoice_id=invoice_id,
                customer=clean_text(
                    row.get("customer")
                ),
                invoice_date=clean_date(
                    row.get("invoice_date")
                ),
                due_date=clean_date(
                    row.get("due_date")
                ),
                amount=clean_float(
                    row.get("amount")
                ),
                currency=clean_text(
                    row.get("currency")
                ),
            )

            session.add(invoice)
            inserted += 1

        else:

            invoice.customer = clean_text(
                row.get("customer")
            )

            invoice.invoice_date = clean_date(
                row.get("invoice_date")
            )

            invoice.due_date = clean_date(
                row.get("due_date")
            )

            invoice.amount = clean_float(
                row.get("amount")
            )

            invoice.currency = clean_text(
                row.get("currency")
            )

            updated += 1

    session.flush()

    print(
        f"[INVOICES] "
        f"Inserted={inserted}, "
        f"Updated={updated}, "
        f"Skipped={skipped}"
    )

    return {
        "inserted": inserted,
        "updated": updated,
        "skipped": skipped,
    }


# ============================================================
# PAYMENT IMPORT
# ============================================================

def import_payments(session):
    """
    Import payments.csv into the payments table.

    The source CSV uses:

        invoice_reference

    while the database model uses:

        payment_invoice_reference
    """

    df = read_csv_file(PAYMENTS_FILE)

    if df.empty:
        return {
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
        }

    inserted = 0
    updated = 0
    skipped = 0

    for _, row in df.iterrows():

        payment_id = clean_text(
            row.get("payment_id")
        )

        if not payment_id:
            skipped += 1
            continue

        invoice_reference = clean_text(
            row.get("invoice_reference")
        )

        # ----------------------------------------------------
        # For normal single-invoice payments, store the
        # invoice ID as the FK.
        #
        # For multi-invoice payments such as:
        #
        # INV-0001|INV-0002|INV-0003
        #
        # there is no single invoice FK.
        # In that case invoice_id is stored as NULL while
        # payment_invoice_reference preserves the full value.
        # ----------------------------------------------------

        invoice_id = None

        if invoice_reference:

            if "|" not in invoice_reference:

                possible_invoice = session.get(
                    Invoice,
                    invoice_reference,
                )

                if possible_invoice is not None:
                    invoice_id = invoice_reference

        payment = session.get(
            Payment,
            payment_id,
        )

        if payment is None:

            payment = Payment(
                payment_id=payment_id,
                invoice_id=invoice_id,
                payment_invoice_reference=invoice_reference,
                customer=clean_text(
                    row.get("customer")
                ),
                payment_date=clean_date(
                    row.get("payment_date")
                ),
                amount=clean_float(
                    row.get("amount")
                ),
                currency=clean_text(
                    row.get("currency")
                ),
                gateway_reference=None,
                payment_fee=clean_float(
                    row.get("fee")
                ),
            )

            session.add(payment)
            inserted += 1

        else:

            payment.invoice_id = invoice_id

            payment.payment_invoice_reference = (
                invoice_reference
            )

            payment.customer = clean_text(
                row.get("customer")
            )

            payment.payment_date = clean_date(
                row.get("payment_date")
            )

            payment.amount = clean_float(
                row.get("amount")
            )

            payment.currency = clean_text(
                row.get("currency")
            )

            payment.payment_fee = clean_float(
                row.get("fee")
            )

            updated += 1

    session.flush()

    print(
        f"[PAYMENTS] "
        f"Inserted={inserted}, "
        f"Updated={updated}, "
        f"Skipped={skipped}"
    )

    return {
        "inserted": inserted,
        "updated": updated,
        "skipped": skipped,
    }


# ============================================================
# BANK TRANSACTION IMPORT
# ============================================================

def import_bank_transactions(session):
    """
    Import bank_transactions.csv.

    Source schema:

        bank_transaction_id
        deposit_date
        amount
        currency
        gateway_reference
    """

    df = read_csv_file(
        BANK_TRANSACTIONS_FILE
    )

    if df.empty:
        return {
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
        }

    inserted = 0
    updated = 0
    skipped = 0

    for _, row in df.iterrows():

        bank_transaction_id = clean_text(
            row.get("bank_transaction_id")
        )

        if not bank_transaction_id:
            skipped += 1
            continue

        bank_transaction = session.get(
            BankTransaction,
            bank_transaction_id,
        )

        if bank_transaction is None:

            bank_transaction = BankTransaction(
                bank_transaction_id=(
                    bank_transaction_id
                ),
                deposit_date=clean_date(
                    row.get("deposit_date")
                ),
                amount=clean_float(
                    row.get("amount")
                ),
                currency=clean_text(
                    row.get("currency")
                ),
            )

            session.add(
                bank_transaction
            )

            inserted += 1

        else:

            bank_transaction.deposit_date = (
                clean_date(
                    row.get("deposit_date")
                )
            )

            bank_transaction.amount = (
                clean_float(
                    row.get("amount")
                )
            )

            bank_transaction.currency = (
                clean_text(
                    row.get("currency")
                )
            )

            updated += 1

    session.flush()

    print(
        f"[BANK TRANSACTIONS] "
        f"Inserted={inserted}, "
        f"Updated={updated}, "
        f"Skipped={skipped}"
    )

    return {
        "inserted": inserted,
        "updated": updated,
        "skipped": skipped,
    }


# ============================================================
# CASE IMPORT
# ============================================================

def import_cases(session, agent_df):
    """
    Import the case-level information generated by TANGLE.
    """

    if agent_df.empty:
        return {
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
        }

    inserted = 0
    updated = 0
    skipped = 0

    for _, row in agent_df.iterrows():

        case_id = clean_text(
            row.get("case_id")
        )

        if not case_id:
            skipped += 1
            continue

        invoice_id = clean_text(
            row.get("invoice_id")
        )

        # Only assign an invoice FK if the invoice
        # actually exists.
        if invoice_id:
            invoice = session.get(
                Invoice,
                invoice_id,
            )

            if invoice is None:
                invoice_id = None

        case = session.get(
            Case,
            case_id,
        )

        values = {
            "record_type": clean_text(
                row.get("record_type")
            ),
            "record_id": clean_text(
                row.get("record_id")
            ),
            "invoice_id": invoice_id,
            "category": clean_text(
                row.get("category")
            ),
            "confidence": clean_float(
                row.get("confidence")
            ),
            "suggested_action": clean_text(
                row.get("suggested_action")
            ),
            "reason": clean_text(
                row.get("reason")
            ),
            "next_action": clean_text(
                row.get("next_action")
            ),
            "payment_amount": clean_float(
                row.get("payment_amount")
            ),
            "bank_amount": clean_float(
                row.get("bank_amount")
            ),
            "payment_fee": clean_float(
                row.get("payment_fee")
            ),
            "outstanding_amount": clean_float(
                row.get("outstanding_amount")
            ),
            "payment_coverage_percent": clean_float(
                row.get("payment_coverage_percent")
            ),
            "bank_payment_difference": clean_float(
                row.get("bank_payment_difference")
            ),
            "invoice_payment_difference": clean_float(
                row.get("invoice_payment_difference")
            ),
            "financial_status": clean_text(
                row.get("financial_status")
            ),
            "financial_impact": clean_text(
                row.get("financial_impact")
            ),
            "original_invoice_amount": clean_float(
                row.get("original_invoice_amount")
            ),
            "decision": clean_text(
                row.get("decision")
            ),
            "decision_confidence": clean_float(
                row.get("decision_confidence")
            ),
            "related_invoice_count": clean_int(
                row.get("related_invoice_count")
            ),
            "related_invoice_ids": clean_text(
                row.get("related_invoice_ids")
            ),
        }

        if case is None:

            case = Case(
                case_id=case_id,
                **values,
            )

            session.add(case)
            inserted += 1

        else:

            for field, value in values.items():
                setattr(
                    case,
                    field,
                    value,
                )

            updated += 1

    session.flush()

    print(
        f"[CASES] "
        f"Inserted={inserted}, "
        f"Updated={updated}, "
        f"Skipped={skipped}"
    )

    return {
        "inserted": inserted,
        "updated": updated,
        "skipped": skipped,
    }


# ============================================================
# INVESTIGATION IMPORT
# ============================================================

def import_investigations(
    session,
    agent_df,
):
    """
    Import AI investigation results.

    One investigation record is maintained per case.
    """

    if agent_df.empty:
        return {
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
        }

    inserted = 0
    updated = 0
    skipped = 0

    for _, row in agent_df.iterrows():

        case_id = clean_text(
            row.get("case_id")
        )

        if not case_id:
            skipped += 1
            continue

        case = session.get(
            Case,
            case_id,
        )

        if case is None:
            skipped += 1
            continue

        investigation = session.execute(
            select(Investigation)
            .where(
                Investigation.case_id
                == case_id
            )
        ).scalars().first()

        values = {
            "hypothesis": clean_text(
                row.get("hypothesis")
            ),
            "investigation_confidence": clean_float(
                row.get(
                    "investigation_confidence"
                )
            ),
            "rationale": clean_text(
                row.get("rationale")
            ),
            "investigation_action": clean_text(
                row.get(
                    "investigation_action"
                )
            ),
            "investigation_finding": clean_text(
                row.get(
                    "investigation_finding"
                )
            ),
            "likely_cause": clean_text(
                row.get("likely_cause")
            ),
            "recommended_action": clean_text(
                row.get(
                    "recommended_action"
                )
            ),
            "reasoning_steps": clean_text(
                row.get("reasoning_steps")
            ),
            "evidence_summary": clean_text(
                row.get("evidence_summary")
            ),
        }

        if investigation is None:

            investigation = Investigation(
                case_id=case_id,
                **values,
            )

            session.add(
                investigation
            )

            inserted += 1

        else:

            for field, value in values.items():
                setattr(
                    investigation,
                    field,
                    value,
                )

            updated += 1

    session.flush()

    print(
        f"[INVESTIGATIONS] "
        f"Inserted={inserted}, "
        f"Updated={updated}, "
        f"Skipped={skipped}"
    )

    return {
        "inserted": inserted,
        "updated": updated,
        "skipped": skipped,
    }


# ============================================================
# RISK ASSESSMENT IMPORT
# ============================================================

def import_risk_assessments(
    session,
    agent_df,
):
    """
    Import TANGLE risk assessment results.

    One risk assessment is maintained per case.
    """

    if agent_df.empty:
        return {
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
        }

    inserted = 0
    updated = 0
    skipped = 0

    for _, row in agent_df.iterrows():

        case_id = clean_text(
            row.get("case_id")
        )

        if not case_id:
            skipped += 1
            continue

        case = session.get(
            Case,
            case_id,
        )

        if case is None:
            skipped += 1
            continue

        risk = session.execute(
            select(RiskAssessment)
            .where(
                RiskAssessment.case_id
                == case_id
            )
        ).scalars().first()

        values = {
            "risk_level": clean_text(
                row.get("risk_level")
            ),
            "priority_score": clean_float(
                row.get("priority_score")
            ),
            "human_review_required": clean_bool(
                row.get(
                    "human_review_required"
                )
            ),
            "risk_reason": clean_text(
                row.get("risk_reason")
            ),
            "financial_impact": clean_text(
                row.get("financial_impact")
            ),
        }

        if risk is None:

            risk = RiskAssessment(
                case_id=case_id,
                **values,
            )

            session.add(risk)
            inserted += 1

        else:

            for field, value in values.items():
                setattr(
                    risk,
                    field,
                    value,
                )

            updated += 1

    session.flush()

    print(
        f"[RISK ASSESSMENTS] "
        f"Inserted={inserted}, "
        f"Updated={updated}, "
        f"Skipped={skipped}"
    )

    return {
        "inserted": inserted,
        "updated": updated,
        "skipped": skipped,
    }


# ============================================================
# REVIEW IMPORT
# ============================================================

def import_reviews(
    session,
    agent_df,
):
    """
    Import human-review lifecycle data.

    review_queue.csv is preferred because it contains
    the actual human review information.

    If review_queue.csv is unavailable, the function does
    nothing rather than inventing review data.
    """

    review_df = read_csv_file(
        REVIEW_QUEUE_FILE
    )

    if review_df.empty:
        print(
            "[REVIEWS] No review_queue.csv "
            "available. Skipping review import."
        )

        return {
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
        }

    inserted = 0
    updated = 0
    skipped = 0

    for _, row in review_df.iterrows():

        case_id = clean_text(
            row.get("case_id")
        )

        if not case_id:
            skipped += 1
            continue

        case = session.get(
            Case,
            case_id,
        )

        if case is None:
            skipped += 1
            continue

        review = session.execute(
            select(Review)
            .where(
                Review.case_id
                == case_id
            )
        ).scalars().first()

        values = {
            "case_status": clean_text(
                row.get("case_status")
            ),
            "review_status": clean_text(
                row.get("review_status")
            ),
            "reviewer_decision": clean_text(
                row.get("reviewer_decision")
            ),
            "reviewer_comment": clean_text(
                row.get("reviewer_comment")
            ),
            "reviewed_at": clean_datetime(
                row.get("reviewed_at")
            ),
            "final_status": clean_text(
                row.get("final_status")
            ),
        }
        # ----------------------------------------------------
        # Synchronize the imported case lifecycle state.
        #
        # review_queue.csv is authoritative for imported
        # human-review lifecycle state.
        # ----------------------------------------------------

        imported_case_status = values["case_status"]

        if imported_case_status:
            case.status = imported_case_status

        if review is None:

            review = Review(
                case_id=case_id,
                **values,
            )

            session.add(review)
            inserted += 1

        else:

            for field, value in values.items():
                setattr(
                    review,
                    field,
                    value,
                )

            updated += 1

    session.flush()

    print(
        f"[REVIEWS] "
        f"Inserted={inserted}, "
        f"Updated={updated}, "
        f"Skipped={skipped}"
    )

    return {
        "inserted": inserted,
        "updated": updated,
        "skipped": skipped,
    }


# ============================================================
# MAIN IMPORT PROCESS
# ============================================================
# ============================================================
# PHASE 10 SOURCE DATA IMPORT
# ============================================================

def import_source_datasets():
    """
    Import only the core Phase 10 source datasets.

    This imports:

        invoices.csv
        payments.csv
        bank_transactions.csv

    It intentionally does NOT import:

        cases
        investigations
        risk assessments
        reviews

    This keeps the Phase 10 ingestion pipeline isolated
    from the existing TANGLE case lifecycle.
    """

    print()
    print("=" * 70)
    print("TANGLE PHASE 10 SOURCE DATA IMPORT")
    print("=" * 70)
    print()

    # --------------------------------------------------------
    # Check required source files
    # --------------------------------------------------------

    required_files = [
        INVOICES_FILE,
        PAYMENTS_FILE,
        BANK_TRANSACTIONS_FILE,
    ]

    missing_files = [
        file
        for file in required_files
        if not file.exists()
    ]

    if missing_files:
        print(
            "[ERROR] The following required source files "
            "are missing:"
        )

        for file in missing_files:
            print(f"       {file}")

        print()

        raise FileNotFoundError(
            "One or more Phase 10 source datasets are missing."
        )

    # --------------------------------------------------------
    # Start database session
    # --------------------------------------------------------

    session = SessionLocal()

    try:
        # ----------------------------------------------------
        # Import invoices
        # ----------------------------------------------------

        print("[PHASE 10] Importing invoices...")

        invoice_result = import_invoices(
            session
        )

        # ----------------------------------------------------
        # Import payments
        # ----------------------------------------------------

        print("[PHASE 10] Importing payments...")

        payment_result = import_payments(
            session
        )

        # ----------------------------------------------------
        # Import bank transactions
        # ----------------------------------------------------

        print(
            "[PHASE 10] Importing bank transactions..."
        )

        bank_result = import_bank_transactions(
            session
        )

        # ----------------------------------------------------
        # Commit all source datasets together
        # ----------------------------------------------------

        session.commit()

        print()
        print("=" * 70)
        print("PHASE 10 SOURCE IMPORT SUCCESSFUL")
        print("=" * 70)
        print()

        print("SUMMARY")
        print("-" * 70)

        print(
            f"Invoices:          "
            f"{invoice_result['inserted']} inserted, "
            f"{invoice_result['updated']} updated, "
            f"{invoice_result['skipped']} skipped"
        )

        print(
            f"Payments:          "
            f"{payment_result['inserted']} inserted, "
            f"{payment_result['updated']} updated, "
            f"{payment_result['skipped']} skipped"
        )

        print(
            f"Bank transactions: "
            f"{bank_result['inserted']} inserted, "
            f"{bank_result['updated']} updated, "
            f"{bank_result['skipped']} skipped"
        )

        print()
        print(
            "Cases, investigations, risk assessments, "
            "and reviews were NOT modified."
        )

        print()

        return {
            "status": "imported",
            "datasets": {
                "invoices": invoice_result,
                "payments": payment_result,
                "bank_transactions": bank_result,
            },
        }

    except Exception:
        # ----------------------------------------------------
        # Roll back everything if any source import fails
        # ----------------------------------------------------

        session.rollback()

        print()
        print("=" * 70)
        print("PHASE 10 SOURCE IMPORT FAILED")
        print("=" * 70)
        print()
        print(
            "All Phase 10 source-data changes were rolled back."
        )
        print()

        raise

    finally:
        session.close()


# ============================================================
# MAIN IMPORT PROCESS
# ============================================================

def import_all_data():


    print()
    print("=" * 70)
    print("TANGLE DATABASE IMPORT")
    print("=" * 70)
    print()

    # --------------------------------------------------------
    # Check required files
    # --------------------------------------------------------

    required_files = [
        INVOICES_FILE,
        PAYMENTS_FILE,
        BANK_TRANSACTIONS_FILE,
        AGENT_RESULTS_FILE,
    ]

    missing_files = [
        file
        for file in required_files
        if not file.exists()
    ]

    if missing_files:

        print(
            "[ERROR] The following required files "
            "are missing:"
        )

        for file in missing_files:
            print(f"       {file}")

        print()
        print(
            "Place the CSV files inside the "
            "TANGLE data folder and run again."
        )

        return

    # --------------------------------------------------------
    # Read agent results once
    # --------------------------------------------------------

    agent_df = read_csv_file(
        AGENT_RESULTS_FILE
    )

    if agent_df.empty:

        print(
            "[ERROR] agent_results.csv is empty."
        )

        return

    # --------------------------------------------------------
    # Start database session
    # --------------------------------------------------------

    session = SessionLocal()

    try:

        # ----------------------------------------------------
        # IMPORTANT:
        #
        # Import parent tables first.
        #
        # invoices
        #      ↓
        # payments
        #      ↓
        # cases
        #      ↓
        # investigations
        # risk assessments
        # reviews
        #
        # This keeps foreign keys valid.
        # ----------------------------------------------------

        invoice_result = import_invoices(
            session
        )

        payment_result = import_payments(
            session
        )

        bank_result = (
            import_bank_transactions(
                session
            )
        )

        case_result = import_cases(
            session,
            agent_df,
        )

        investigation_result = (
            import_investigations(
                session,
                agent_df,
            )
        )

        risk_result = (
            import_risk_assessments(
                session,
                agent_df,
            )
        )

        review_result = import_reviews(
            session,
            agent_df,
        )

        # ----------------------------------------------------
        # Commit everything together.
        # ----------------------------------------------------

        session.commit()

        print()
        print("=" * 70)
        print("DATABASE IMPORT SUCCESSFUL")
        print("=" * 70)

        print()
        print("SUMMARY")
        print("-" * 70)

        print(
            f"Invoices:             "
            f"{invoice_result['inserted']} inserted, "
            f"{invoice_result['updated']} updated"
        )

        print(
            f"Payments:             "
            f"{payment_result['inserted']} inserted, "
            f"{payment_result['updated']} updated"
        )

        print(
            f"Bank transactions:    "
            f"{bank_result['inserted']} inserted, "
            f"{bank_result['updated']} updated"
        )

        print(
            f"Cases:                "
            f"{case_result['inserted']} inserted, "
            f"{case_result['updated']} updated"
        )

        print(
            f"Investigations:       "
            f"{investigation_result['inserted']} inserted, "
            f"{investigation_result['updated']} updated"
        )

        print(
            f"Risk assessments:     "
            f"{risk_result['inserted']} inserted, "
            f"{risk_result['updated']} updated"
        )

        print(
            f"Reviews:              "
            f"{review_result['inserted']} inserted, "
            f"{review_result['updated']} updated"
        )

        print()
        print("=" * 70)
        print("TANGLE PostgreSQL database is ready.")
        print("=" * 70)
        print()

    except Exception as error:

        # ----------------------------------------------------
        # If anything fails, undo EVERYTHING from this import.
        # ----------------------------------------------------

        session.rollback()

        print()
        print("=" * 70)
        print("DATABASE IMPORT FAILED")
        print("=" * 70)
        print()
        print(error)
        print()
        print(
            "All changes from this import were rolled back."
        )
        print()

        raise

    finally:

        session.close()


# ============================================================
# ENTRY POINT
# ============================================================


if __name__ == "__main__":
    import_all_data()
