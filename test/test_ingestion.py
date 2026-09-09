from pathlib import Path
import shutil

import pytest

from backend.services.ingestion_service import (
    activate_staged_dataset,
    validate_staged_dataset_quality,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
STAGING_DIR = PROJECT_ROOT / "staging"


@pytest.fixture
def clean_invoice_staging():
    """Prepare a clean invoices.csv in staging and restore it afterward."""
    active_path = DATA_DIR / "invoices.csv"
    staging_path = STAGING_DIR / "invoices.csv"

    original_staging = (
        staging_path.read_text(encoding="utf-8")
        if staging_path.exists()
        else None
    )

    shutil.copy2(active_path, staging_path)

    try:
        yield staging_path
    finally:
        if original_staging is not None:
            staging_path.write_text(
                original_staging,
                encoding="utf-8",
            )
        elif staging_path.exists():
            staging_path.unlink()


def remove_currency_column(staging_path):
    """Remove the required currency column from the staged CSV."""
    lines = staging_path.read_text(encoding="utf-8").splitlines()

    header = lines[0].split(",")
    currency_index = header.index("currency")

    modified_header = [
        column
        for index, column in enumerate(header)
        if index != currency_index
    ]

    modified_rows = []

    for line in lines[1:]:
        values = line.split(",")

        modified_rows.append(
            ",".join(
                value
                for index, value in enumerate(values)
                if index != currency_index
            )
        )

    staging_path.write_text(
        ",".join(modified_header)
        + "\n"
        + "\n".join(modified_rows)
        + "\n",
        encoding="utf-8",
    )


def test_valid_staged_dataset_can_activate(clean_invoice_staging):
    """A valid staged dataset should activate successfully."""
    result = activate_staged_dataset("invoices")

    assert result["dataset"] == "invoices"

    assert result["validation"]["errors"] == 0

    assert result["validation"]["activation_allowed"] is True

    assert (DATA_DIR / "invoices.csv").exists()


def test_missing_required_column_blocks_activation(clean_invoice_staging):
    """A staged dataset missing a required column must not activate."""
    staging_path = clean_invoice_staging

    remove_currency_column(staging_path)

    with pytest.raises(Exception):
        activate_staged_dataset("invoices")


def test_quality_errors_block_activation(clean_invoice_staging):
    """Structural validation errors must prevent activation."""
    staging_path = clean_invoice_staging

    remove_currency_column(staging_path)

    quality = validate_staged_dataset_quality("invoices")

    assert quality["errors"] > 0
    assert quality["activation_allowed"] is False

    with pytest.raises(Exception):
        activate_staged_dataset("invoices")


def test_failed_activation_does_not_replace_active_dataset(
    clean_invoice_staging,
):
    """Failed activation must leave the active dataset untouched."""
    active_path = DATA_DIR / "invoices.csv"
    staging_path = clean_invoice_staging

    original_active = active_path.read_text(encoding="utf-8")

    remove_currency_column(staging_path)

    with pytest.raises(Exception):
        activate_staged_dataset("invoices")

    assert active_path.read_text(encoding="utf-8") == original_active

def test_source_import_only_updates_source_datasets():
    """Phase 10 import must only import the three source datasets."""
    from database.import_data import import_source_datasets

    result = import_source_datasets()

    assert result["status"] == "imported"

    assert set(result["datasets"].keys()) == {
        "invoices",
        "payments",
        "bank_transactions",
    }

    for dataset_result in result["datasets"].values():
        assert dataset_result["inserted"] >= 0
        assert dataset_result["updated"] >= 0
        assert dataset_result["skipped"] >= 0