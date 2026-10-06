from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from backend.services.data_quality_service import (
    run_data_quality_check,
    run_staged_data_quality_check,
)
from database.import_data import import_source_datasets
from generator.generate_data import run_reconciliation as generate_reconciliation
from generator.generate_data import run_reconciliation as generate_reconciliation


BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data"
STAGING_DIR = BASE_DIR / "staging"


SUPPORTED_DATASETS = {
    "invoices": "invoices.csv",
    "payments": "payments.csv",
    "bank_transactions": "bank_transactions.csv",
}


def ensure_directories() -> None:
    """
    Ensure the active and staging directories exist.
    """
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    STAGING_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


def normalize_dataset_name(
    dataset_name: str,
) -> str:
    """
    Normalize and validate a dataset name.
    """
    normalized_name = dataset_name.strip().lower()

    if normalized_name not in SUPPORTED_DATASETS:
        supported = ", ".join(
            SUPPORTED_DATASETS.keys()
        )

        raise ValueError(
            f"Unsupported dataset: {dataset_name}. "
            f"Supported datasets are: {supported}."
        )

    return normalized_name


def get_dataset_filename(
    dataset_name: str,
) -> str:
    """
    Return the CSV filename for a supported dataset.
    """
    dataset_name = normalize_dataset_name(
        dataset_name
    )

    return SUPPORTED_DATASETS[dataset_name]


def get_dataset_path(
    dataset_name: str,
) -> Path:
    """
    Return the active dataset path.
    """
    filename = get_dataset_filename(
        dataset_name
    )

    return DATA_DIR / filename


def get_staging_path(
    dataset_name: str,
) -> Path:
    """
    Return the staging dataset path.
    """
    filename = get_dataset_filename(
        dataset_name
    )

    return STAGING_DIR / filename


def save_uploaded_dataset(
    dataset_name: str,
    uploaded_file: Any,
) -> dict:
    """
    Save an uploaded CSV file into staging.

    The active dataset is never modified by this function.
    """
    ensure_directories()

    dataset_name = normalize_dataset_name(
        dataset_name
    )

    filename = get_dataset_filename(
        dataset_name
    )

    staging_path = STAGING_DIR / filename

    file_contents = uploaded_file.file.read()

    if not file_contents:
        raise ValueError(
            "Uploaded file is empty."
        )

    staging_path.write_bytes(
        file_contents
    )

    try:
        dataframe = pd.read_csv(
            staging_path
        )
    except Exception as exc:
        staging_path.unlink(
            missing_ok=True
        )

        raise ValueError(
            f"Uploaded file is not a valid CSV: {exc}"
        ) from exc

    return {
        "dataset": dataset_name,
        "filename": filename,
        "path": str(staging_path),
        "size_bytes": len(file_contents),
        "storage": "staging",
        "validation": {
            "dataset": dataset_name,
            "filename": filename,
            "rows": len(dataframe),
            "columns": len(dataframe.columns),
            "column_names": list(
                dataframe.columns
            ),
        },
    }


def validate_staged_dataset(
    dataset_name: str,
) -> dict:
    """
    Perform structural validation on a staged dataset.

    This checks:

    - file existence
    - CSV readability
    - required columns
    - unexpected columns

    This function does NOT run the complete
    TANGLE Data Quality Engine.
    """
    ensure_directories()

    dataset_name = normalize_dataset_name(
        dataset_name
    )

    staging_path = get_staging_path(
        dataset_name
    )

    if not staging_path.exists():
        raise FileNotFoundError(
            f"Staged dataset not found: {staging_path}"
        )

    try:
        dataframe = pd.read_csv(
            staging_path
        )
    except Exception as exc:
        raise ValueError(
            f"Unable to read staged CSV: {exc}"
        ) from exc

    expected_columns = {
        "invoices": {
            "invoice_id",
            "customer",
            "invoice_date",
            "due_date",
            "amount",
            "currency",
        },
        "payments": {
            "payment_id",
            "invoice_reference",
            "customer",
            "payment_date",
            "amount",
            "currency",
            "fee",
            "original_invoice_amount",
        },
        "bank_transactions": {
            "bank_transaction_id",
            "deposit_date",
            "amount",
            "currency",
            "gateway_reference",
        },
    }

    required_columns = expected_columns[
        dataset_name
    ]

    actual_columns = set(
        dataframe.columns
    )

    missing_columns = sorted(
        required_columns - actual_columns
    )

    unexpected_columns = sorted(
        actual_columns - required_columns
    )

    is_valid = (
        len(missing_columns) == 0
        and len(unexpected_columns) == 0
    )

    return {
        "dataset": dataset_name,
        "status": (
            "valid"
            if is_valid
            else "invalid"
        ),
        "filename": staging_path.name,
        "rows": len(dataframe),
        "columns": len(dataframe.columns),
        "column_names": list(
            dataframe.columns
        ),
        "missing_columns": missing_columns,
        "unexpected_columns": unexpected_columns,
    }


def validate_staged_dataset_quality(
    dataset_name: str,
) -> dict:
    """
    Run the full TANGLE Data Quality Engine
    against a staged dataset.

    The staged dataset is validated together
    with the other active datasets inside a
    temporary directory.

    The active datasets are never modified.
    """
    ensure_directories()

    dataset_name = normalize_dataset_name(
        dataset_name
    )

    return run_staged_data_quality_check(
        dataset_name
    )


def activate_staged_dataset(
    dataset_name: str,
) -> dict:
    """
    Activate a staged dataset only when the
    full Data Quality Engine reports zero errors.

    Warnings are allowed.

    The staged file replaces the active file
    only after successful validation.
    """
    ensure_directories()

    dataset_name = normalize_dataset_name(
        dataset_name
    )

    staging_path = get_staging_path(
        dataset_name
    )

    active_path = get_dataset_path(
        dataset_name
    )

    if not staging_path.exists():
        raise FileNotFoundError(
            f"Staged dataset not found: {staging_path}"
        )

    # ---------------------------------------------------------
    # STEP 1: Structural validation
    # ---------------------------------------------------------

    structural_validation = (
        validate_staged_dataset(
            dataset_name
        )
    )

    if structural_validation["status"] != "valid":
        raise ValueError(
            "Staged dataset failed structural validation. "
            "Activation blocked."
        )

    # ---------------------------------------------------------
    # STEP 2: Full Data Quality validation
    # ---------------------------------------------------------

    quality_validation = (
        validate_staged_dataset_quality(
            dataset_name
        )
    )

    if quality_validation["errors"] > 0:
        raise ValueError(
            "Staged dataset failed Data Quality validation. "
            "Activation blocked."
        )

    # ---------------------------------------------------------
    # STEP 3: Activate
    # ---------------------------------------------------------

    # Replace the active file only after validation succeeds.
    staging_path.replace(
        active_path
    )

    return {
        "dataset": dataset_name,
        "filename": active_path.name,
        "path": str(active_path),
        "storage": "active",
        "status": "activated",
        "validation": {
            "quality_score": quality_validation[
                "quality_score"
            ],
            "total_records": quality_validation[
                "total_records"
            ],
            "valid_records": quality_validation[
                "valid_records"
            ],
            "warnings": quality_validation[
                "warnings"
            ],
            "errors": quality_validation[
                "errors"
            ],
            "activation_allowed": quality_validation[
                "activation_allowed"
            ],
        },
    }


def run_ingestion_quality_check() -> dict:
    """
    Run the full Data Quality Engine against
    the currently active datasets.
    """
    ensure_directories()

    return run_data_quality_check(
        data_dir=DATA_DIR
    )


def get_ingestion_status() -> dict:
    """
    Return the current status of active and
    staged datasets.
    """
    ensure_directories()

    datasets = {}

    for dataset_name, filename in (
        SUPPORTED_DATASETS.items()
    ):
        active_path = DATA_DIR / filename
        staging_path = STAGING_DIR / filename

        datasets[dataset_name] = {
            "filename": filename,
            "active": {
                "exists": active_path.exists(),
                "path": str(active_path),
                "size_bytes": (
                    active_path.stat().st_size
                    if active_path.exists()
                    else 0
                ),
            },
            "staging": {
                "exists": staging_path.exists(),
                "path": str(staging_path),
                "size_bytes": (
                    staging_path.stat().st_size
                    if staging_path.exists()
                    else 0
                ),
            },
        }

    return {
        "datasets": datasets
    }


def import_active_datasets():
    """
    Import the currently active source datasets
    into PostgreSQL.

    This imports only:

        invoices
        payments
        bank_transactions

    It does not modify:

        cases
        investigations
        risk assessments
        reviews
    """
    result = import_source_datasets()

    generate_reconciliation()

    result["reconciliation_status"] = "generated"

    return result
