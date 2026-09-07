import pandas as pd
from rapidfuzz import fuzz
from itertools import combinations
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

AMOUNT_TOLERANCE = 0.02
DATE_WINDOW_DAYS = 5
REFERENCE_THRESHOLD = 70

MAX_SUBSET_SIZE = 3


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    invoices = pd.read_csv(
        DATA_DIR / "invoices.csv"
    )

    payments = pd.read_csv(
        DATA_DIR / "payments.csv"
    )

    bank = pd.read_csv(
        DATA_DIR / "bank_transactions.csv"
    )

    ground_truth = pd.read_csv(
        DATA_DIR / "ground_truth.csv"
    )

    invoices["invoice_date"] = pd.to_datetime(
        invoices["invoice_date"]
    )

    invoices["due_date"] = pd.to_datetime(
        invoices["due_date"]
    )

    payments["payment_date"] = pd.to_datetime(
        payments["payment_date"]
    )

    bank["deposit_date"] = pd.to_datetime(
        bank["deposit_date"]
    )

    return invoices, payments, bank, ground_truth


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def amount_close(a, b, tolerance=AMOUNT_TOLERANCE):

    return abs(float(a) - float(b)) <= tolerance


def date_close(date1, date2, days=DATE_WINDOW_DAYS):

    difference = abs(
        (pd.Timestamp(date1) - pd.Timestamp(date2)).days
    )

    return difference <= days


def reference_similarity(ref1, ref2):

    if pd.isna(ref1) or pd.isna(ref2):
        return 0

    return fuzz.ratio(
        str(ref1).upper(),
        str(ref2).upper()
    )


# ============================================================
# SUBSET SUM
# ============================================================

def find_subset(records, target, amount_column="amount"):

    """
    Find up to MAX_SUBSET_SIZE records whose
    amounts approximately equal target.
    """

    if records.empty:
        return None

    records = records.reset_index(drop=False)

    values = records[amount_column].astype(float).tolist()

    max_size = min(
        MAX_SUBSET_SIZE,
        len(values)
    )

    for size in range(2, max_size + 1):

        for indexes in combinations(
            range(len(values)),
            size
        ):

            total = sum(
                values[i]
                for i in indexes
            )

            if amount_close(
                total,
                target,
                tolerance=AMOUNT_TOLERANCE
            ):

                return records.iloc[
                    list(indexes)
                ]

    return None


# ============================================================
# PASS 1
# DETERMINISTIC MATCHING
# ============================================================

def pass_one_exact_matching(
    invoices,
    payments,
    bank
):

    matches = []

    matched_invoices = set()
    matched_payments = set()
    matched_bank = set()

    # --------------------------------------------------------
    # Invoice → Payment
    # --------------------------------------------------------

    for _, invoice in invoices.iterrows():

        for _, payment in payments.iterrows():

            if payment["payment_id"] in matched_payments:
                continue

            if invoice["invoice_id"] != payment["invoice_reference"]:
                continue

            if invoice["currency"] != payment["currency"]:
                continue

            # Exact amount
            if amount_close(
                invoice["amount"],
                payment["amount"]
            ) and payment["fee"] == 0:

                matches.append({
                    "invoice_id":
                        invoice["invoice_id"],

                    "payment_id":
                        payment["payment_id"],

                    "bank_transaction_id":
                        None,

                    "pass":
                        1,

                    "match_type":
                        "EXACT",

                    "confidence":
                        1.00,

                    "rationale":
                        "Exact invoice reference and amount match."
                })

                matched_invoices.add(
                    invoice["invoice_id"]
                )

                matched_payments.add(
                    payment["payment_id"]
                )

                break

    # --------------------------------------------------------
    # Payment → Bank
    # --------------------------------------------------------

    for _, payment in payments.iterrows():

        if payment["payment_id"] not in matched_payments:
            continue

        for _, bank_row in bank.iterrows():

            if bank_row["bank_transaction_id"] in matched_bank:
                continue

            if (
                bank_row["gateway_reference"]
                == payment["payment_id"]
                and
                bank_row["currency"]
                == payment["currency"]
                and
                amount_close(
                    bank_row["amount"],
                    payment["amount"]
                )
            ):

                # Find the corresponding match
                for match in matches:

                    if (
                        match["payment_id"]
                        == payment["payment_id"]
                    ):

                        match[
                            "bank_transaction_id"
                        ] = bank_row[
                            "bank_transaction_id"
                        ]

                matched_bank.add(
                    bank_row[
                        "bank_transaction_id"
                    ]
                )

                break

    return (
        matches,
        matched_invoices,
        matched_payments,
        matched_bank
    )


# ============================================================
# PASS 2A
# FUZZY INVOICE → PAYMENT
# ============================================================

def fuzzy_invoice_payment_matching(
    invoices,
    payments,
    matched_invoices,
    matched_payments
):

    matches = []

    for _, invoice in invoices.iterrows():

        if invoice["invoice_id"] in matched_invoices:
            continue

        best_match = None
        best_score = 0

        for _, payment in payments.iterrows():

            if payment["payment_id"] in matched_payments:
                continue

            if invoice["currency"] != payment["currency"]:
                continue

            similarity = reference_similarity(
                invoice["invoice_id"],
                payment["invoice_reference"]
            )

            date_match = date_close(
                invoice["due_date"],
                payment["payment_date"]
            )

            amount_difference = abs(
                float(invoice["amount"])
                -
                float(payment["original_invoice_amount"])
            )

            # Allow fee differences
            amount_match = (
                amount_difference
                <= invoice["amount"] * 0.05
            )

            if (
                similarity >= REFERENCE_THRESHOLD
                and
                date_match
                and
                amount_match
            ):

                score = (
                    0.50 * (similarity / 100)
                    +
                    0.30 * (1 if date_match else 0)
                    +
                    0.20 * (
                        1
                        -
                        min(
                            amount_difference
                            /
                            max(
                                float(invoice["amount"]),
                                1
                            ),
                            1
                        )
                    )
                )

                if score > best_score:

                    best_score = score
                    best_match = payment

        if best_match is not None:

            matches.append({
                "invoice_id":
                    invoice["invoice_id"],

                "payment_id":
                    best_match["payment_id"],

                "bank_transaction_id":
                    None,

                "pass":
                    2,

                "match_type":
                    "FUZZY",

                "confidence":
                    round(best_score, 3),

                "rationale":
                    "Matched using reference similarity, "
                    "date proximity and amount tolerance."
            })

            matched_invoices.add(
                invoice["invoice_id"]
            )

            matched_payments.add(
                best_match["payment_id"]
            )

    return matches


# ============================================================
# PASS 2B
# MERGED PAYMENT DETECTION
# ============================================================

def merged_payment_matching(
    invoices,
    payments,
    matched_invoices,
    matched_payments
):

    matches = []

    available_invoices = invoices[
        ~invoices["invoice_id"].isin(
            matched_invoices
        )
    ].copy()

    available_payments = payments[
        ~payments["payment_id"].isin(
            matched_payments
        )
    ].copy()

    for _, payment in available_payments.iterrows():

        payment_amount = float(
            payment["original_invoice_amount"]
        )

        subset = find_subset(
            available_invoices,
            payment_amount,
            "amount"
        )

        if subset is None:
            continue

        invoice_ids = []

        for _, invoice in subset.iterrows():

            invoice_id = invoice[
                "invoice_id"
            ]

            invoice_ids.append(
                invoice_id
            )

            matched_invoices.add(
                invoice_id
            )

        matched_payments.add(
            payment["payment_id"]
        )

        for invoice_id in invoice_ids:

            matches.append({
                "invoice_id":
                    invoice_id,

                "payment_id":
                    payment["payment_id"],

                "bank_transaction_id":
                    None,

                "pass":
                    2,

                "match_type":
                    "MERGED_PAYMENT",

                "confidence":
                    0.92,

                "rationale":
                    "Multiple invoice amounts combine "
                    "to the payment amount."
            })

    return matches


# ============================================================
# PASS 2C
# SPLIT PAYMENT DETECTION
# ============================================================

def split_payment_matching(
    invoices,
    payments,
    matched_invoices,
    matched_payments
):

    matches = []

    available_invoices = invoices[
        ~invoices["invoice_id"].isin(
            matched_invoices
        )
    ].copy()

    available_payments = payments[
        ~payments["payment_id"].isin(
            matched_payments
        )
    ].copy()

    for _, invoice in available_invoices.iterrows():

        invoice_amount = float(
            invoice["amount"]
        )

        candidates = available_payments[
            available_payments["currency"]
            ==
            invoice["currency"]
        ].copy()

        subset = find_subset(
            candidates,
            invoice_amount,
            "original_invoice_amount"
        )

        if subset is None:
            continue

        for _, payment in subset.iterrows():

            matches.append({
                "invoice_id":
                    invoice["invoice_id"],

                "payment_id":
                    payment["payment_id"],

                "bank_transaction_id":
                    None,

                "pass":
                    2,

                "match_type":
                    "SPLIT_PAYMENT",

                "confidence":
                    0.90,

                "rationale":
                    "Multiple payments combine "
                    "to the invoice amount."
            })

            matched_payments.add(
                payment["payment_id"]
            )

        matched_invoices.add(
            invoice["invoice_id"]
        )

    return matches


# ============================================================
# PASS 2D
# PAYMENT → BANK
# ============================================================

def payment_bank_matching(
    payments,
    bank,
    matches,
    matched_payments,
    matched_bank
):

    for _, payment in payments.iterrows():

        if payment["payment_id"] not in matched_payments:
            continue

        # Already linked
        already_linked = any(
            m["payment_id"] == payment["payment_id"]
            and
            m["bank_transaction_id"] is not None
            for m in matches
        )

        if already_linked:
            continue

        best_bank = None
        best_score = 0

        for _, bank_row in bank.iterrows():

            if (
                bank_row["bank_transaction_id"]
                in matched_bank
            ):
                continue

            if (
                bank_row["currency"]
                != payment["currency"]
            ):
                continue

            similarity = reference_similarity(
                payment["payment_id"],
                bank_row["gateway_reference"]
            )

            date_match = date_close(
                payment["payment_date"],
                bank_row["deposit_date"],
                days=3
            )

            payment_amount = float(
                payment["amount"]
            )

            bank_amount = float(
                bank_row["amount"]
            )

            amount_difference = abs(
                payment_amount
                -
                bank_amount
            )

            # Fees can cause small difference
            amount_match = (
                amount_difference
                <=
                max(
                    payment_amount * 0.03,
                    1
                )
            )

            if (
                date_match
                and
                amount_match
            ):

                score = (
                    0.4 * (similarity / 100)
                    +
                    0.3 * int(date_match)
                    +
                    0.3 * int(amount_match)
                )

                if score > best_score:

                    best_score = score
                    best_bank = bank_row

        if best_bank is not None:

            bank_id = best_bank[
                "bank_transaction_id"
            ]

            for match in matches:

                if (
                    match["payment_id"]
                    ==
                    payment["payment_id"]
                    and
                    match[
                        "bank_transaction_id"
                    ]
                    is None
                ):

                    match[
                        "bank_transaction_id"
                    ] = bank_id

            matched_bank.add(
                bank_id
            )


# ============================================================
# EXCEPTION DETECTION
# ============================================================

def generate_exceptions(
    invoices,
    payments,
    bank,
    matches,
    matched_invoices,
    matched_payments,
    matched_bank
):

    exceptions = []

    # --------------------------------------------------------
    # Unmatched invoices
    # --------------------------------------------------------

    for _, invoice in invoices.iterrows():

        if invoice["invoice_id"] not in matched_invoices:

            exceptions.append({
                "record_type":
                    "INVOICE",

                "record_id":
                    invoice["invoice_id"],

                "amount":
                    invoice["amount"],

                "category":
                    "MISSING_PAYMENT",

                "confidence":
                    0.0,

                "suggested_action":
                    "Investigate unpaid invoice."
            })

    # --------------------------------------------------------
    # Unmatched payments
    # --------------------------------------------------------

    for _, payment in payments.iterrows():

        if payment["payment_id"] not in matched_payments:

            reference = str(
                payment["invoice_reference"]
            )

            if "MISSING" in reference:

                category = "MISSING_INVOICE"

            else:

                category = "UNEXPLAINED_PAYMENT"

            exceptions.append({
                "record_type":
                    "PAYMENT",

                "record_id":
                    payment["payment_id"],

                "amount":
                    payment["amount"],

                "category":
                    category,

                "confidence":
                    0.0,

                "suggested_action":
                    "Investigate payment against ERP."
            })

    # --------------------------------------------------------
    # Unmatched bank deposits
    # --------------------------------------------------------

    for _, bank_row in bank.iterrows():

        bank_id = bank_row[
            "bank_transaction_id"
        ]

        if bank_id not in matched_bank:

            if (
                str(
                    bank_row["gateway_reference"]
                )
                .startswith("UNKNOWN")
            ):

                category = "UNKNOWN_DEPOSIT"

            else:

                category = "UNRECONCILED_BANK"

            exceptions.append({
                "record_type":
                    "BANK",

                "record_id":
                    bank_id,

                "amount":
                    bank_row["amount"],

                "category":
                    category,

                "confidence":
                    0.0,

                "suggested_action":
                    "Investigate bank deposit."
            })

    return pd.DataFrame(exceptions)


# ============================================================
# METRICS
# ============================================================

def calculate_metrics(
    invoices,
    payments,
    bank,
    matches,
    exceptions
):

    total_invoices = len(invoices)

    total_payments = len(payments)

    total_bank = len(bank)

    total_matches = len(matches)

    exact_matches = len([
        m for m in matches
        if m["pass"] == 1
    ])

    fuzzy_matches = len([
        m for m in matches
        if m["pass"] == 2
    ])

    exception_count = len(exceptions)

    invoice_match_rate = (
        len(
            set(
                m["invoice_id"]
                for m in matches
            )
        )
        /
        total_invoices
        if total_invoices
        else 0
    )

    return {
        "total_invoices":
            total_invoices,

        "total_payments":
            total_payments,

        "total_bank_transactions":
            total_bank,

        "total_match_relationships":
            total_matches,

        "pass_1_exact_matches":
            exact_matches,

        "pass_2_matches":
            fuzzy_matches,

        "exceptions":
            exception_count,

        "invoice_match_rate":
            round(
                invoice_match_rate,
                4
            )
    }


# ============================================================
# MAIN ENGINE
# ============================================================

def run_reconciliation():

    print("\n======================================")
    print("TANGLE RECONCILIATION ENGINE")
    print("======================================")

    invoices, payments, bank, ground_truth = load_data()

    print("\nData loaded:")
    print("Invoices:", len(invoices))
    print("Payments:", len(payments))
    print("Bank:", len(bank))

    # --------------------------------------------------------
    # PASS 1
    # --------------------------------------------------------

    print("\nRunning PASS 1 - Exact matching...")

    (
        matches,
        matched_invoices,
        matched_payments,
        matched_bank
    ) = pass_one_exact_matching(
        invoices,
        payments,
        bank
    )

    print(
        "Pass 1 matches:",
        len(matches)
    )

    # --------------------------------------------------------
    # PASS 2A
    # --------------------------------------------------------

    print("\nRunning PASS 2A - Fuzzy matching...")

    fuzzy_matches = fuzzy_invoice_payment_matching(
        invoices,
        payments,
        matched_invoices,
        matched_payments
    )

    matches.extend(
        fuzzy_matches
    )

    print(
        "Fuzzy matches:",
        len(fuzzy_matches)
    )

    # --------------------------------------------------------
    # PASS 2B
    # --------------------------------------------------------

    print("\nRunning PASS 2B - Merged payments...")

    merged_matches = merged_payment_matching(
        invoices,
        payments,
        matched_invoices,
        matched_payments
    )

    matches.extend(
        merged_matches
    )

    print(
        "Merged relationships:",
        len(merged_matches)
    )

    # --------------------------------------------------------
    # PASS 2C
    # --------------------------------------------------------

    print("\nRunning PASS 2C - Split payments...")

    split_matches = split_payment_matching(
        invoices,
        payments,
        matched_invoices,
        matched_payments
    )

    matches.extend(
        split_matches
    )

    print(
        "Split relationships:",
        len(split_matches)
    )

    # --------------------------------------------------------
    # PAYMENT → BANK
    # --------------------------------------------------------

    print("\nMatching gateway → bank...")

    payment_bank_matching(
        payments,
        bank,
        matches,
        matched_payments,
        matched_bank
    )

    # --------------------------------------------------------
    # EXCEPTIONS
    # --------------------------------------------------------

    exceptions = generate_exceptions(
        invoices,
        payments,
        bank,
        matches,
        matched_invoices,
        matched_payments,
        matched_bank
    )

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    metrics = calculate_metrics(
        invoices,
        payments,
        bank,
        matches,
        exceptions
    )

    # --------------------------------------------------------
    # SAVE RESULTS
    # --------------------------------------------------------

    results_df = pd.DataFrame(
        matches
    )

    results_df.to_csv(
        DATA_DIR / "reconciliation_results.csv",
        index=False
    )

    exceptions.to_csv(
        DATA_DIR / "exceptions.csv",
        index=False
    )

    pd.DataFrame(
        [metrics]
    ).to_csv(
        DATA_DIR / "metrics.csv",
        index=False
    )

    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    print("\n======================================")
    print("RECONCILIATION COMPLETE")
    print("======================================")

    print(
        f"Exact matches:       {metrics['pass_1_exact_matches']}"
    )

    print(
        f"Pass 2 matches:      {metrics['pass_2_matches']}"
    )

    print(
        f"Exceptions:          {metrics['exceptions']}"
    )

    print(
        f"Invoice match rate:  "
        f"{metrics['invoice_match_rate'] * 100:.2f}%"
    )

    print("\nGenerated files:")

    print(
        "data/reconciliation_results.csv"
    )

    print(
        "data/exceptions.csv"
    )

    print(
        "data/metrics.csv"
    )


if __name__ == "__main__":

    run_reconciliation()