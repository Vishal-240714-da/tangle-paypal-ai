from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INVOICES_FILE = PROJECT_ROOT / "data" / "invoices.csv"
PAYMENTS_FILE = PROJECT_ROOT / "data" / "payments.csv"
BANK_TRANSACTIONS_FILE = PROJECT_ROOT / "data" / "bank_transactions.csv"
RECONCILIATION_FILE = PROJECT_ROOT / "data" / "reconciliation_results.csv"


RECONCILIATION_REQUIRED_COLUMNS = {
    "invoice_id",
    "payment_id",
    "bank_transaction_id",
    "pass",
    "match_type",
    "confidence",
    "rationale",
}

INVOICE_REQUIRED_COLUMNS = {
    "invoice_id",
    "amount",
    "currency",
    "invoice_date",
}

PAYMENT_REQUIRED_COLUMNS = {
    "payment_id",
    "invoice_reference",
    "amount",
    "currency",
    "payment_date",
}

BANK_REQUIRED_COLUMNS = {
    "bank_transaction_id",
    "amount",
    "currency",
    "deposit_date",
}


@dataclass
class ReconciliationRecord:
    invoice_id: str | None
    payment_id: str | None
    bank_transaction_id: str | None

    pass_status: int
    match_type: str
    confidence: float
    rationale: str

    invoice_amount: float | None
    invoice_currency: str | None
    invoice_date: str | None

    payment_amount: float | None
    payment_currency: str | None
    payment_date: str | None

    bank_amount: float | None
    bank_currency: str | None
    bank_date: str | None

    payment_invoice_difference: float | None
    bank_payment_difference: float | None
    payment_coverage_percent: float | None


@dataclass
class ReconciliationSummary:
    total: int
    exact: int
    fuzzy: int
    merged_payment: int
    failed: int
    average_confidence: float


@dataclass
class ReconciliationResult:
    items: list[dict]
    total: int
    summary: dict


def _clean_id(value) -> str | None:
    if pd.isna(value):
        return None

    value = str(value).strip()

    if not value:
        return None

    return value


def _clean_text(value) -> str | None:
    if pd.isna(value):
        return None

    value = str(value).strip()

    if not value:
        return None

    return value


def _safe_float(value) -> float | None:
    if pd.isna(value):
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _round(value: float | None, digits: int = 2) -> float | None:
    if value is None:
        return None

    return round(value, digits)


def _validate_columns(
    dataframe: pd.DataFrame,
    required_columns: set[str],
    dataset_name: str,
) -> None:
    missing_columns = required_columns - set(dataframe.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))

        raise ValueError(
            f"{dataset_name} is missing required columns: {missing}"
        )


def _load_source_data() -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    files = [
        INVOICES_FILE,
        PAYMENTS_FILE,
        BANK_TRANSACTIONS_FILE,
        RECONCILIATION_FILE,
    ]

    missing_files = [
        str(path)
        for path in files
        if not path.exists()
    ]

    if missing_files:
        raise FileNotFoundError(
            "Reconciliation source file(s) not found: "
            + ", ".join(missing_files)
        )

    invoices = pd.read_csv(INVOICES_FILE)
    payments = pd.read_csv(PAYMENTS_FILE)
    bank_transactions = pd.read_csv(BANK_TRANSACTIONS_FILE)
    reconciliation = pd.read_csv(RECONCILIATION_FILE)

    _validate_columns(
        invoices,
        INVOICE_REQUIRED_COLUMNS,
        "invoices.csv",
    )

    _validate_columns(
        payments,
        PAYMENT_REQUIRED_COLUMNS,
        "payments.csv",
    )

    _validate_columns(
        bank_transactions,
        BANK_REQUIRED_COLUMNS,
        "bank_transactions.csv",
    )

    _validate_columns(
        reconciliation,
        RECONCILIATION_REQUIRED_COLUMNS,
        "reconciliation_results.csv",
    )

    return (
        invoices,
        payments,
        bank_transactions,
        reconciliation,
    )


def _build_lookup(
    dataframe: pd.DataFrame,
    key: str,
) -> dict[str, dict]:
    lookup: dict[str, dict] = {}

    for record in dataframe.to_dict(orient="records"):
        record_id = _clean_id(record.get(key))

        if record_id is not None:
            lookup[record_id] = record

    return lookup


def _calculate_coverage(
    invoice_amount: float | None,
    payment_amount: float | None,
) -> float | None:
    if (
        invoice_amount is None
        or payment_amount is None
        or invoice_amount == 0
    ):
        return None

    return _round(
        (payment_amount / invoice_amount) * 100,
        2,
    )


def _build_record(
    reconciliation_row: dict,
    invoices: dict[str, dict],
    payments: dict[str, dict],
    bank_transactions: dict[str, dict],
) -> ReconciliationRecord:
    invoice_id = _clean_id(
        reconciliation_row.get("invoice_id")
    )

    payment_id = _clean_id(
        reconciliation_row.get("payment_id")
    )

    bank_transaction_id = _clean_id(
        reconciliation_row.get("bank_transaction_id")
    )

    invoice = invoices.get(invoice_id, {})
    payment = payments.get(payment_id, {})
    bank = bank_transactions.get(bank_transaction_id, {})

    invoice_amount = _safe_float(
        invoice.get("amount")
    )

    payment_amount = _safe_float(
        payment.get("amount")
    )

    bank_amount = _safe_float(
        bank.get("amount")
    )

    payment_invoice_difference = None

    if (
        invoice_amount is not None
        and payment_amount is not None
    ):
        payment_invoice_difference = _round(
            payment_amount - invoice_amount
        )

    bank_payment_difference = None

    if (
        bank_amount is not None
        and payment_amount is not None
    ):
        bank_payment_difference = _round(
            bank_amount - payment_amount
        )

    return ReconciliationRecord(
        invoice_id=invoice_id,
        payment_id=payment_id,
        bank_transaction_id=bank_transaction_id,

        pass_status=int(
            reconciliation_row.get("pass", 0)
        ),

        match_type=(
            _clean_text(
                reconciliation_row.get("match_type")
            )
            or "UNKNOWN"
        ),

        confidence=(
            _safe_float(
                reconciliation_row.get("confidence")
            )
            or 0.0
        ),

        rationale=(
            _clean_text(
                reconciliation_row.get("rationale")
            )
            or ""
        ),

        invoice_amount=invoice_amount,
        invoice_currency=_clean_text(
            invoice.get("currency")
        ),
        invoice_date=_clean_text(
            invoice.get("invoice_date")
        ),

        payment_amount=payment_amount,
        payment_currency=_clean_text(
            payment.get("currency")
        ),
        payment_date=_clean_text(
            payment.get("payment_date")
        ),

        bank_amount=bank_amount,
        bank_currency=_clean_text(
            bank.get("currency")
        ),
        bank_date=_clean_text(
            bank.get("deposit_date")
        ),

        payment_invoice_difference=payment_invoice_difference,

        bank_payment_difference=bank_payment_difference,

        payment_coverage_percent=_calculate_coverage(
            invoice_amount,
            payment_amount,
        ),
    )


def run_reconciliation() -> ReconciliationResult:
    (
        invoices_df,
        payments_df,
        bank_transactions_df,
        reconciliation_df,
    ) = _load_source_data()

    invoices = _build_lookup(
        invoices_df,
        "invoice_id",
    )

    payments = _build_lookup(
        payments_df,
        "payment_id",
    )

    bank_transactions = _build_lookup(
        bank_transactions_df,
        "bank_transaction_id",
    )

    records: list[dict] = []

    for row in reconciliation_df.to_dict(
        orient="records"
    ):
        record = _build_record(
            row,
            invoices,
            payments,
            bank_transactions,
        )

        records.append(
            asdict(record)
        )

    total = len(records)

    exact = sum(
        1
        for record in records
        if record["match_type"] == "EXACT"
    )

    fuzzy = sum(
        1
        for record in records
        if record["match_type"] == "FUZZY"
    )

    merged_payment = sum(
        1
        for record in records
        if record["match_type"] == "MERGED_PAYMENT"
    )

    failed = sum(
        1
        for record in records
        if record["pass_status"] != 1
    )

    confidence_values = [
        record["confidence"]
        for record in records
    ]

    average_confidence = (
        _round(
            sum(confidence_values)
            / len(confidence_values),
            4,
        )
        if confidence_values
        else 0.0
    )

    summary = ReconciliationSummary(
        total=total,
        exact=exact,
        fuzzy=fuzzy,
        merged_payment=merged_payment,
        failed=failed,
        average_confidence=average_confidence,
    )

    return ReconciliationResult(
        items=records,
        total=total,
        summary=asdict(summary),
    )


if __name__ == "__main__":
    result = run_reconciliation()

    print(
        "Reconciliation records:",
        result.total,
    )

    print(
        "Summary:",
        result.summary,
    )

    print(
        "\nFirst record:"
    )

    print(
        result.items[0]
    )