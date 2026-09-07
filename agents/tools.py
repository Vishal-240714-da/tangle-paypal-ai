import pandas as pd
from pathlib import Path
from itertools import combinations


# ============================================================
# PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


# ============================================================
# LOAD DATA
# ============================================================

def load_all_data():

    invoices = pd.read_csv(
        DATA_DIR / "invoices.csv"
    )

    payments = pd.read_csv(
        DATA_DIR / "payments.csv"
    )

    bank = pd.read_csv(
        DATA_DIR / "bank_transactions.csv"
    )

    return invoices, payments, bank


# ============================================================
# TOOL 1 — FIND INVOICE
# ============================================================

def find_invoice(invoice_id):

    invoices, _, _ = load_all_data()

    result = invoices[
        invoices["invoice_id"]
        .astype(str)
        .str.upper()
        ==
        str(invoice_id).upper()
    ]

    if result.empty:

        return {
            "found": False,
            "message": "Invoice not found."
        }

    return {
        "found": True,
        "invoice": result.iloc[0].to_dict()
    }


# ============================================================
# TOOL 2 — FIND PAYMENT
# ============================================================

def find_payment(payment_id):

    _, payments, _ = load_all_data()

    result = payments[
        payments["payment_id"]
        .astype(str)
        .str.upper()
        ==
        str(payment_id).upper()
    ]

    if result.empty:

        return {
            "found": False,
            "message": "Payment not found."
        }

    return {
        "found": True,
        "payment": result.iloc[0].to_dict()
    }


# ============================================================
# TOOL 3 — FIND BANK TRANSACTION
# ============================================================

def find_bank_transaction(bank_id):

    _, _, bank = load_all_data()

    result = bank[
        bank["bank_transaction_id"]
        .astype(str)
        .str.upper()
        ==
        str(bank_id).upper()
    ]

    if result.empty:

        return {
            "found": False,
            "message": "Bank transaction not found."
        }

    return {
        "found": True,
        "bank_transaction":
            result.iloc[0].to_dict()
    }


# ============================================================
# TOOL 4 — CALCULATE DIFFERENCE
# ============================================================

def calculate_difference(
    expected_amount,
    actual_amount
):

    expected_amount = float(expected_amount)
    actual_amount = float(actual_amount)

    difference = actual_amount - expected_amount

    percentage = (
        abs(difference)
        /
        expected_amount
        * 100
        if expected_amount != 0
        else 0
    )

    return {
        "expected_amount":
            expected_amount,

        "actual_amount":
            actual_amount,

        "difference":
            round(difference, 2),

        "percentage_difference":
            round(percentage, 2)
    }


# ============================================================
# TOOL 5 — FIND INVOICE COMBINATION
# ============================================================

def find_invoice_combination(
    target_amount,
    currency,
    max_items=3
):

    invoices, _, _ = load_all_data()

    candidates = invoices[
        invoices["currency"]
        ==
        currency
    ].copy()

    # Keep the search manageable
    candidates = candidates.head(50)

    target_amount = float(
        target_amount
    )

    records = candidates.to_dict(
        "records"
    )

    for size in range(
        2,
        min(
            max_items,
            len(records)
        ) + 1
    ):

        for combination in combinations(
            records,
            size
        ):

            total = sum(
                float(item["amount"])
                for item in combination
            )

            if abs(
                total - target_amount
            ) <= 0.02:

                return {
                    "found": True,

                    "target":
                        target_amount,

                    "invoices":
                        combination,

                    "combined_amount":
                        round(total, 2)
                }

    return {
        "found": False,

        "target":
            target_amount,

        "message":
            "No invoice combination found."
    }


# ============================================================
# TOOL 6 — FX CALCULATION
# ============================================================

FX_RATES = {

    ("USD", "INR"):
        83.0,

    ("EUR", "INR"):
        90.0,

    ("INR", "USD"):
        1 / 83.0,

    ("INR", "EUR"):
        1 / 90.0,

    ("USD", "EUR"):
        83.0 / 90.0,

    ("EUR", "USD"):
        90.0 / 83.0
}


def calculate_fx(
    amount,
    from_currency,
    to_currency
):

    amount = float(amount)

    if from_currency == to_currency:

        return {
            "amount":
                amount,

            "rate":
                1,

            "converted_amount":
                amount
        }

    rate = FX_RATES.get(
        (
            from_currency,
            to_currency
        )
    )

    if rate is None:

        return {
            "error":
                "FX rate unavailable."
        }

    converted = amount * rate

    return {

        "amount":
            amount,

        "from_currency":
            from_currency,

        "to_currency":
            to_currency,

        "rate":
            rate,

        "converted_amount":
            round(
                converted,
                2
            )
    }


# ============================================================
# TOOL 7 — DUPLICATE CHECK
# ============================================================

def check_duplicate_payment(
    payment_id
):

    _, payments, _ = load_all_data()

    payment = payments[
        payments["payment_id"]
        ==
        payment_id
    ]

    if payment.empty:

        return {
            "duplicate":
                False
        }

    reference = payment.iloc[0][
        "invoice_reference"
    ]

    amount = payment.iloc[0][
        "amount"
    ]

    similar = payments[
        (
            payments[
                "invoice_reference"
            ]
            ==
            reference
        )
        &
        (
            payments[
                "amount"
            ]
            ==
            amount
        )
    ]

    return {

        "duplicate":
            len(similar) > 1,

        "matching_records":
            len(similar)
    }


# ============================================================
# TOOL 8 — FEE ANALYSIS
# ============================================================

def analyze_fee(
    invoice_amount,
    payment_amount
):

    invoice_amount = float(
        invoice_amount
    )

    payment_amount = float(
        payment_amount
    )

    difference = (
        invoice_amount
        -
        payment_amount
    )

    percentage = (
        difference
        /
        invoice_amount
        * 100
        if invoice_amount != 0
        else 0
    )

    return {

        "invoice_amount":
            invoice_amount,

        "payment_amount":
            payment_amount,

        "possible_fee":
            round(
                difference,
                2
            ),

        "fee_percentage":
            round(
                percentage,
                2
            ),

        "looks_like_processing_fee":
            0 <= percentage <= 5
    }


# ============================================================
# QUICK TEST
# ============================================================

if __name__ == "__main__":

    print("Tangle tools loaded successfully.")

    invoices, payments, bank = load_all_data()

    print(
        "Invoices:",
        len(invoices)
    )

    print(
        "Payments:",
        len(payments)
    )

    print(
        "Bank transactions:",
        len(bank)
    )
# ============================================================
# FIND PAYMENTS BY AMOUNT
# ============================================================

def find_payments_by_amount(amount, tolerance=2.0):

    payments = load_payments()

    if payments.empty:
        return []

    amount_column = get_amount_column(payments)

    if amount_column is None:
        return []

    payments[amount_column] = pd.to_numeric(
        payments[amount_column],
        errors="coerce"
    )

    matches = payments[
        (
            payments[amount_column] - float(amount)
        ).abs() <= tolerance
    ]

    return matches.to_dict("records")


# ============================================================
# FIND BANK TRANSACTIONS BY AMOUNT
# ============================================================

def find_bank_by_amount(amount, tolerance=2.0):

    bank = load_bank()

    if bank.empty:
        return []

    amount_column = get_amount_column(bank)

    if amount_column is None:
        return []

    bank[amount_column] = pd.to_numeric(
        bank[amount_column],
        errors="coerce"
    )

    matches = bank[
        (
            bank[amount_column] - float(amount)
        ).abs() <= tolerance
    ]

    return matches.to_dict("records")

