
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data"
STAGING_DIR = BASE_DIR / "staging"

SUPPORTED_CURRENCIES = {
    "INR",
    "USD",
    "EUR",
    "GBP",
}


# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class QualityIssue:
    dataset: str
    record_id: str | None
    issue_type: str
    severity: str
    message: str


@dataclass
class QualityResult:
    dataset: str
    total_records: int
    valid_records: int
    warnings: int
    errors: int
    issues: list[QualityIssue] = field(
        default_factory=list
    )


# ============================================================
# GENERAL HELPERS
# ============================================================

def _is_missing(value: Any) -> bool:
    """
    Return True when a value is empty or NaN.
    """

    if value is None:
        return True

    try:
        if pd.isna(value):
            return True
    except Exception:
        pass

    return str(value).strip() == ""


def _record_id(value: Any) -> str | None:
    """
    Convert an ID value into a clean string.
    """

    if _is_missing(value):
        return None

    return str(value).strip()


# ============================================================
# STRUCTURE VALIDATION
# ============================================================

def _validate_dataframe_structure(
    df: pd.DataFrame,
    dataset: str,
    required_columns: list[str],
    id_column: str,
) -> list[QualityIssue]:

    issues: list[QualityIssue] = []

    # --------------------------------------------------------
    # Required columns
    # --------------------------------------------------------

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        issues.append(
            QualityIssue(
                dataset=dataset,
                record_id=None,
                issue_type="MALFORMED_RECORD",
                severity="ERROR",
                message=(
                    "Missing required columns: "
                    + ", ".join(missing_columns)
                ),
            )
        )

    # --------------------------------------------------------
    # Missing IDs
    # --------------------------------------------------------

    if id_column in df.columns:

        for index, value in df[id_column].items():

            if _is_missing(value):

                issues.append(
                    QualityIssue(
                        dataset=dataset,
                        record_id=None,
                        issue_type="MISSING_ID",
                        severity="ERROR",
                        message=(
                            f"Missing {id_column} "
                            f"at row {index + 2}."
                        ),
                    )
                )

        # ----------------------------------------------------
        # Duplicate IDs
        # ----------------------------------------------------

        duplicate_mask = (
            df[id_column].duplicated(
                keep=False
            )
            & df[id_column].notna()
        )

        for index, value in df.loc[
            duplicate_mask,
            id_column,
        ].items():

            issues.append(
                QualityIssue(
                    dataset=dataset,
                    record_id=_record_id(value),
                    issue_type="DUPLICATE_RECORD",
                    severity="ERROR",
                    message=(
                        f"Duplicate {id_column}: "
                        f"{value}."
                    ),
                )
            )

    return issues


# ============================================================
# AMOUNT VALIDATION
# ============================================================

def _validate_amounts(
    df: pd.DataFrame,
    dataset: str,
    id_column: str,
    amount_columns: list[str],
) -> list[QualityIssue]:

    issues: list[QualityIssue] = []

    for column in amount_columns:

        if column not in df.columns:
            continue

        for index, value in df[column].items():

            record_id = (
                _record_id(
                    df.at[index, id_column]
                )
                if id_column in df.columns
                else None
            )

            # ------------------------------------------------
            # Missing amount
            # ------------------------------------------------

            if _is_missing(value):

                issues.append(
                    QualityIssue(
                        dataset=dataset,
                        record_id=record_id,
                        issue_type="INVALID_AMOUNT",
                        severity="ERROR",
                        message=(
                            f"Missing amount in "
                            f"{column}."
                        ),
                    )
                )

                continue

            # ------------------------------------------------
            # Non-numeric amount
            # ------------------------------------------------

            try:
                numeric_value = float(value)

            except (TypeError, ValueError):

                issues.append(
                    QualityIssue(
                        dataset=dataset,
                        record_id=record_id,
                        issue_type="INVALID_AMOUNT",
                        severity="ERROR",
                        message=(
                            f"Invalid numeric amount "
                            f"in {column}: {value}."
                        ),
                    )
                )

                continue

            # ------------------------------------------------
            # Negative values
            # ------------------------------------------------

            if numeric_value < 0:

                issues.append(
                    QualityIssue(
                        dataset=dataset,
                        record_id=record_id,
                        issue_type="NEGATIVE_VALUE",
                        severity="ERROR",
                        message=(
                            f"Negative value in "
                            f"{column}: "
                            f"{numeric_value}."
                        ),
                    )
                )

    return issues


# ============================================================
# DATE VALIDATION
# ============================================================

def _validate_dates(
    df: pd.DataFrame,
    dataset: str,
    id_column: str,
    date_columns: list[str],
) -> list[QualityIssue]:

    issues: list[QualityIssue] = []

    for column in date_columns:

        if column not in df.columns:
            continue

        for index, value in df[column].items():

            record_id = (
                _record_id(
                    df.at[index, id_column]
                )
                if id_column in df.columns
                else None
            )

            # ------------------------------------------------
            # Missing date
            # ------------------------------------------------

            if _is_missing(value):

                issues.append(
                    QualityIssue(
                        dataset=dataset,
                        record_id=record_id,
                        issue_type="INVALID_DATE",
                        severity="ERROR",
                        message=(
                            f"Missing date in "
                            f"{column}."
                        ),
                    )
                )

                continue

            # ------------------------------------------------
            # Invalid date
            # ------------------------------------------------

            parsed = pd.to_datetime(
                value,
                errors="coerce",
            )

            if pd.isna(parsed):

                issues.append(
                    QualityIssue(
                        dataset=dataset,
                        record_id=record_id,
                        issue_type="INVALID_DATE",
                        severity="ERROR",
                        message=(
                            f"Invalid date in "
                            f"{column}: "
                            f"{value}."
                        ),
                    )
                )

    return issues


# ============================================================
# CURRENCY VALIDATION
# ============================================================

def _validate_currencies(
    df: pd.DataFrame,
    dataset: str,
    id_column: str,
) -> list[QualityIssue]:

    issues: list[QualityIssue] = []

    if "currency" not in df.columns:
        return issues

    for index, value in df["currency"].items():

        record_id = (
            _record_id(
                df.at[index, id_column]
            )
            if id_column in df.columns
            else None
        )

        # ----------------------------------------------------
        # Missing currency
        # ----------------------------------------------------

        if _is_missing(value):

            issues.append(
                QualityIssue(
                    dataset=dataset,
                    record_id=record_id,
                    issue_type="CURRENCY_PROBLEM",
                    severity="WARNING",
                    message="Currency is missing.",
                )
            )

            continue

        currency = str(
            value
        ).strip().upper()

        # ----------------------------------------------------
        # Unsupported currency
        # ----------------------------------------------------

        if currency not in SUPPORTED_CURRENCIES:

            issues.append(
                QualityIssue(
                    dataset=dataset,
                    record_id=record_id,
                    issue_type="CURRENCY_PROBLEM",
                    severity="WARNING",
                    message=(
                        f"Unsupported currency: "
                        f"{currency}."
                    ),
                )
            )

    return issues


# ============================================================
# RELATIONSHIP VALIDATION
# ============================================================

def _validate_relationships(
    invoices: pd.DataFrame,
    payments: pd.DataFrame,
    bank_transactions: pd.DataFrame,
) -> list[QualityIssue]:

    issues: list[QualityIssue] = []

    # --------------------------------------------------------
    # Build reference sets
    # --------------------------------------------------------

    invoice_ids = set(
        invoices["invoice_id"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    payment_ids = set(
        payments["payment_id"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    bank_payment_refs = set(
        bank_transactions["gateway_reference"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    # ========================================================
    # PAYMENT → INVOICE
    # ========================================================

    for _, row in payments.iterrows():

        payment_id = _record_id(
            row.get("payment_id")
        )

        invoice_reference = _record_id(
            row.get("invoice_reference")
        )

        # ----------------------------------------------------
        # Missing invoice reference
        # ----------------------------------------------------

        if not invoice_reference:

            issues.append(
                QualityIssue(
                    dataset="payments",
                    record_id=payment_id,
                    issue_type="MISSING_RELATIONSHIP",
                    severity="WARNING",
                    message=(
                        "Payment has no "
                        "invoice reference."
                    ),
                )
            )

            continue

        # ----------------------------------------------------
        # Multi-invoice payments
        # ----------------------------------------------------

        references = [
            reference.strip()
            for reference in invoice_reference.split("|")
            if reference.strip()
        ]

        missing_references = [
            reference
            for reference in references
            if reference not in invoice_ids
        ]

        if missing_references:

            issues.append(
                QualityIssue(
                    dataset="payments",
                    record_id=payment_id,
                    issue_type="MISSING_RELATIONSHIP",
                    severity="WARNING",
                    message=(
                        "Payment references missing "
                        "invoice(s): "
                        + ", ".join(
                            missing_references
                        )
                    ),
                )
            )

    # ========================================================
    # BANK TRANSACTION → PAYMENT
    # ========================================================

    for _, row in bank_transactions.iterrows():

        bank_id = _record_id(
            row.get("bank_transaction_id")
        )

        gateway_reference = _record_id(
            row.get("gateway_reference")
        )

        # ----------------------------------------------------
        # Missing payment reference
        # ----------------------------------------------------

        if not gateway_reference:

            issues.append(
                QualityIssue(
                    dataset="bank_transactions",
                    record_id=bank_id,
                    issue_type="MISSING_RELATIONSHIP",
                    severity="WARNING",
                    message=(
                        "Bank transaction has no "
                        "payment reference."
                    ),
                )
            )

            continue

        # ----------------------------------------------------
        # Unknown payment reference
        # ----------------------------------------------------

        if gateway_reference not in payment_ids:

            issues.append(
                QualityIssue(
                    dataset="bank_transactions",
                    record_id=bank_id,
                    issue_type="MISSING_RELATIONSHIP",
                    severity="WARNING",
                    message=(
                        "Bank transaction references "
                        f"missing payment "
                        f"{gateway_reference}."
                    ),
                )
            )

    # ========================================================
    # PAYMENT WITHOUT BANK TRANSACTION
    # ========================================================

    missing_bank_relationships = (
        payment_ids - bank_payment_refs
    )

    for payment_id in sorted(
        missing_bank_relationships
    ):

        issues.append(
            QualityIssue(
                dataset="payments",
                record_id=payment_id,
                issue_type="MISSING_RELATIONSHIP",
                severity="WARNING",
                message=(
                    f"Payment {payment_id} has no "
                    "matching bank transaction."
                ),
            )
        )

    return issues


# ============================================================
# DATASET VALIDATION
# ============================================================

def _validate_dataset(
    df: pd.DataFrame,
    dataset: str,
    required_columns: list[str],
    id_column: str,
    amount_columns: list[str],
    date_columns: list[str],
) -> QualityResult:

    issues: list[QualityIssue] = []

    # --------------------------------------------------------
    # Structure
    # --------------------------------------------------------

    issues.extend(
        _validate_dataframe_structure(
            df=df,
            dataset=dataset,
            required_columns=required_columns,
            id_column=id_column,
        )
    )

    # --------------------------------------------------------
    # Amounts
    # --------------------------------------------------------

    issues.extend(
        _validate_amounts(
            df=df,
            dataset=dataset,
            id_column=id_column,
            amount_columns=amount_columns,
        )
    )

    # --------------------------------------------------------
    # Dates
    # --------------------------------------------------------

    issues.extend(
        _validate_dates(
            df=df,
            dataset=dataset,
            id_column=id_column,
            date_columns=date_columns,
        )
    )

    # --------------------------------------------------------
    # Currency
    # --------------------------------------------------------

    issues.extend(
        _validate_currencies(
            df=df,
            dataset=dataset,
            id_column=id_column,
        )
    )

    # --------------------------------------------------------
    # Counts
    # --------------------------------------------------------

    error_count = sum(
        issue.severity == "ERROR"
        for issue in issues
    )

    warning_count = sum(
        issue.severity == "WARNING"
        for issue in issues
    )

    affected_records = {
        issue.record_id
        for issue in issues
        if issue.record_id is not None
    }

    valid_records = max(
        len(df) - len(affected_records),
        0,
    )

    return QualityResult(
        dataset=dataset,
        total_records=len(df),
        valid_records=valid_records,
        warnings=warning_count,
        errors=error_count,
        issues=issues,
    )


# ============================================================
# LOAD DATASETS
# ============================================================

def _load_datasets(
    data_dir: Path,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    """
    Load the three core TANGLE datasets from a directory.
    """

    data_dir = Path(data_dir)

    invoices_file = (
        data_dir / "invoices.csv"
    )

    payments_file = (
        data_dir / "payments.csv"
    )

    bank_transactions_file = (
        data_dir / "bank_transactions.csv"
    )

    missing_files = [
        path
        for path in [
            invoices_file,
            payments_file,
            bank_transactions_file,
        ]
        if not path.exists()
    ]

    if missing_files:

        missing_names = ", ".join(
            path.name
            for path in missing_files
        )

        raise FileNotFoundError(
            "Required dataset file(s) missing: "
            + missing_names
        )

    invoices = pd.read_csv(
        invoices_file
    )

    payments = pd.read_csv(
        payments_file
    )

    bank_transactions = pd.read_csv(
        bank_transactions_file
    )

    return (
        invoices,
        payments,
        bank_transactions,
    )


# ============================================================
# MAIN DATA QUALITY ENGINE
# ============================================================

def run_data_quality_check(
    data_dir: Path | None = None,
) -> dict[str, Any]:
    """
    Run the TANGLE Data Quality Engine.

    Default:
        validates active data/

    Optional:
        validates another directory.

    This allows the exact same quality engine to be used
    for staged datasets without modifying active data.
    """

    if data_dir is None:
        data_dir = DATA_DIR

    data_dir = Path(data_dir)

    # --------------------------------------------------------
    # Load datasets
    # --------------------------------------------------------

    (
        invoices,
        payments,
        bank_transactions,
    ) = _load_datasets(
        data_dir
    )

    # ========================================================
    # INVOICES
    # ========================================================

    invoice_result = _validate_dataset(
        df=invoices,
        dataset="invoices",
        required_columns=[
            "invoice_id",
            "customer",
            "invoice_date",
            "due_date",
            "amount",
            "currency",
        ],
        id_column="invoice_id",
        amount_columns=[
            "amount",
        ],
        date_columns=[
            "invoice_date",
            "due_date",
        ],
    )

    # ========================================================
    # PAYMENTS
    # ========================================================

    payment_result = _validate_dataset(
        df=payments,
        dataset="payments",
        required_columns=[
            "payment_id",
            "invoice_reference",
            "customer",
            "payment_date",
            "amount",
            "currency",
            "fee",
            "original_invoice_amount",
        ],
        id_column="payment_id",
        amount_columns=[
            "amount",
            "fee",
            "original_invoice_amount",
        ],
        date_columns=[
            "payment_date",
        ],
    )

    # ========================================================
    # BANK TRANSACTIONS
    # ========================================================

    bank_result = _validate_dataset(
        df=bank_transactions,
        dataset="bank_transactions",
        required_columns=[
            "bank_transaction_id",
            "deposit_date",
            "amount",
            "currency",
            "gateway_reference",
        ],
        id_column="bank_transaction_id",
        amount_columns=[
            "amount",
        ],
        date_columns=[
            "deposit_date",
        ],
    )

    # ========================================================
    # RELATIONSHIPS
    # ========================================================

    relationship_issues = _validate_relationships(
        invoices=invoices,
        payments=payments,
        bank_transactions=bank_transactions,
    )

    # ========================================================
    # COMBINE RESULTS
    # ========================================================

    all_results = [
        invoice_result,
        payment_result,
        bank_result,
    ]

    all_issues = [
        issue
        for result in all_results
        for issue in result.issues
    ]

    all_issues.extend(
        relationship_issues
    )

    # ========================================================
    # GLOBAL METRICS
    # ========================================================

    total_records = sum(
        result.total_records
        for result in all_results
    )

    affected_records = {
        (
            issue.dataset,
            issue.record_id,
        )
        for issue in all_issues
        if issue.record_id is not None
    }

    valid_records = max(
        total_records
        - len(affected_records),
        0,
    )

    errors = sum(
        issue.severity == "ERROR"
        for issue in all_issues
    )

    warnings = sum(
        issue.severity == "WARNING"
        for issue in all_issues
    )

    # ========================================================
    # QUALITY SCORE
    # ========================================================

    if total_records == 0:

        quality_score = 100.0

    else:

        quality_score = round(
            (
                valid_records
                / total_records
            ) * 100,
            2,
        )

    # ========================================================
    # ISSUE TYPE SUMMARY
    # ========================================================

    issue_type_counts: dict[
        str,
        int,
    ] = {}

    for issue in all_issues:

        issue_type_counts[
            issue.issue_type
        ] = (
            issue_type_counts.get(
                issue.issue_type,
                0,
            )
            + 1
        )

    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    return {
        "quality_score": quality_score,
        "total_records": total_records,
        "valid_records": valid_records,
        "warnings": warnings,
        "errors": errors,

        "datasets": {
            result.dataset: {
                "total_records": (
                    result.total_records
                ),
                "valid_records": (
                    result.valid_records
                ),
                "warnings": result.warnings,
                "errors": result.errors,
            }
            for result in all_results
        },

        "issue_summary": issue_type_counts,

        "issues": [
            {
                "dataset": issue.dataset,
                "record_id": issue.record_id,
                "issue_type": issue.issue_type,
                "severity": issue.severity,
                "message": issue.message,
            }
            for issue in all_issues
        ],
    }


# ============================================================
# STAGED DATASET VALIDATION HELPER
# ============================================================

def run_staged_data_quality_check(
    dataset_name: str,
) -> dict[str, Any]:
    """
    Validate a staged dataset safely.

    The staged dataset replaces only that dataset inside
    a temporary validation directory.

    The other two datasets come from the active data
    directory.

    The active data directory is never modified.
    """

    import shutil
    import tempfile

    dataset_name = (
        dataset_name
        .strip()
        .lower()
    )

    supported_datasets = {
        "invoices": "invoices.csv",
        "payments": "payments.csv",
        "bank_transactions": (
            "bank_transactions.csv"
        ),
    }

    if dataset_name not in supported_datasets:

        raise ValueError(
            f"Unsupported dataset: "
            f"{dataset_name}. Supported datasets are: "
            f"{', '.join(supported_datasets.keys())}."
        )

    staged_file = (
        STAGING_DIR
        / supported_datasets[dataset_name]
    )

    if not staged_file.exists():

        raise FileNotFoundError(
            f"Staged dataset not found: "
            f"{staged_file}"
        )

    temporary_directory = Path(
        tempfile.mkdtemp(
            prefix="tangle_quality_"
        )
    )

    try:

        # ----------------------------------------------------
        # Copy active datasets into temporary directory.
        # ----------------------------------------------------

        for filename in supported_datasets.values():

            active_file = (
                DATA_DIR / filename
            )

            if not active_file.exists():

                raise FileNotFoundError(
                    f"Active dataset not found: "
                    f"{active_file}"
                )

            shutil.copy2(
                active_file,
                temporary_directory / filename,
            )

        # ----------------------------------------------------
        # Replace the selected dataset with its staged version.
        # ----------------------------------------------------

        shutil.copy2(
            staged_file,
            temporary_directory
            / supported_datasets[dataset_name],
        )

        # ----------------------------------------------------
        # Run the complete existing quality engine.
        # ----------------------------------------------------

        quality_result = (
            run_data_quality_check(
                data_dir=temporary_directory
            )
        )

        # ----------------------------------------------------
        # Add ingestion-specific metadata.
        # ----------------------------------------------------

        quality_result["dataset"] = (
            dataset_name
        )

        quality_result["filename"] = (
            staged_file.name
        )

        quality_result["storage"] = (
            "staging"
        )

        quality_result["validation_type"] = (
            "full_data_quality"
        )

        # ----------------------------------------------------
        # Activation rule
        #
        # Warnings are allowed.
        # Errors block activation.
        # ----------------------------------------------------

        quality_result[
            "activation_allowed"
        ] = (
            quality_result["errors"] == 0
        )

        return quality_result

    finally:

        # ----------------------------------------------------
        # Always delete temporary validation directory.
        # ----------------------------------------------------

        shutil.rmtree(
            temporary_directory,
            ignore_errors=True,
        )


# ============================================================
# DIRECT EXECUTION
# ============================================================

if __name__ == "__main__":

    import json

    result = run_data_quality_check()

    print(
        json.dumps(
            result,
            indent=2,
        )
    )