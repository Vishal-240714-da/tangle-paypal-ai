from pathlib import Path
import shutil

import pytest

from backend.services.ingestion_service import (
    activate_staged_dataset,
    get_dataset_filename,
    get_dataset_path,
    get_ingestion_status,
    get_staging_path,
    import_active_datasets,
    normalize_dataset_name,
    run_ingestion_quality_check,
    save_uploaded_dataset,
    validate_staged_dataset,
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


# ---------------------------------------------------------------------------
# Dataset name / path tests
# ---------------------------------------------------------------------------


def test_normalize_dataset_name_accepts_supported_names():
    assert normalize_dataset_name("invoices") == "invoices"
    assert normalize_dataset_name("payments") == "payments"
    assert normalize_dataset_name("bank_transactions") == "bank_transactions"


def test_normalize_dataset_name_strips_spaces_and_lowercases():
    assert normalize_dataset_name("  INVOICES  ") == "invoices"
    assert normalize_dataset_name(" Payments ") == "payments"
    assert normalize_dataset_name(" BANK_TRANSACTIONS ") == "bank_transactions"


def test_normalize_dataset_name_rejects_unsupported_dataset():
    with pytest.raises(
        ValueError,
        match="Unsupported dataset",
    ):
        normalize_dataset_name("customers")


def test_dataset_filename_mapping():
    assert get_dataset_filename("invoices") == "invoices.csv"
    assert get_dataset_filename("payments") == "payments.csv"
    assert get_dataset_filename("bank_transactions") == "bank_transactions.csv"


def test_dataset_paths_point_to_expected_directories():
    assert get_dataset_path("invoices") == DATA_DIR / "invoices.csv"
    assert get_staging_path("invoices") == STAGING_DIR / "invoices.csv"


# ---------------------------------------------------------------------------
# Structural validation tests
# ---------------------------------------------------------------------------


def test_validate_staged_dataset_accepts_valid_invoice_dataset(
    clean_invoice_staging,
):
    result = validate_staged_dataset("invoices")

    assert result["dataset"] == "invoices"
    assert result["status"] == "valid"
    assert result["filename"] == "invoices.csv"
    assert result["rows"] > 0
    assert result["columns"] == 6
    assert result["missing_columns"] == []
    assert result["unexpected_columns"] == []


def test_validate_staged_dataset_accepts_dataset_name_normalization(
    clean_invoice_staging,
):
    result = validate_staged_dataset("  INVOICES  ")

    assert result["dataset"] == "invoices"
    assert result["status"] == "valid"


def test_validate_staged_dataset_rejects_missing_staged_file():
    staging_path = STAGING_DIR / "invoices.csv"

    original = (
        staging_path.read_bytes()
        if staging_path.exists()
        else None
    )

    try:
        if staging_path.exists():
            staging_path.unlink()

        with pytest.raises(
            FileNotFoundError,
            match="Staged dataset not found",
        ):
            validate_staged_dataset("invoices")
    finally:
        if original is not None:
            staging_path.write_bytes(original)


def test_validate_staged_dataset_rejects_invalid_csv(
    clean_invoice_staging,
):
    clean_invoice_staging.write_text(
        "invoice_id,amount,currency\n"
        '"broken,row\n',
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Unable to read staged CSV",
    ):
        validate_staged_dataset("invoices")


def test_validate_staged_dataset_detects_unexpected_column(
    clean_invoice_staging,
):
    original = clean_invoice_staging.read_text(encoding="utf-8")

    try:
        lines = original.splitlines()
        lines[0] = lines[0] + ",unexpected_column"

        modified_rows = []

        for line in lines[1:]:
            modified_rows.append(line + ",TEST")

        clean_invoice_staging.write_text(
            "\n".join(
                [lines[0]] + modified_rows
            )
            + "\n",
            encoding="utf-8",
        )

        result = validate_staged_dataset("invoices")

        assert result["status"] == "invalid"
        assert "unexpected_column" in result["unexpected_columns"]
    finally:
        clean_invoice_staging.write_text(
            original,
            encoding="utf-8",
        )


def test_validate_staged_dataset_detects_missing_required_column(
    clean_invoice_staging,
):
    remove_currency_column(clean_invoice_staging)

    result = validate_staged_dataset("invoices")

    assert result["status"] == "invalid"
    assert result["missing_columns"] == ["currency"]


# ---------------------------------------------------------------------------
# Full Data Quality validation
# ---------------------------------------------------------------------------


def test_validate_staged_dataset_quality_returns_quality_result(
    clean_invoice_staging,
):
    result = validate_staged_dataset_quality("invoices")

    assert result["dataset"] == "invoices"
    assert "quality_score" in result
    assert "total_records" in result
    assert "valid_records" in result
    assert "warnings" in result
    assert "errors" in result
    assert "activation_allowed" in result


def test_validate_staged_dataset_quality_does_not_modify_active_dataset(
    clean_invoice_staging,
):
    active_path = DATA_DIR / "invoices.csv"
    original_active = active_path.read_bytes()

    validate_staged_dataset_quality("invoices")

    assert active_path.read_bytes() == original_active


# ---------------------------------------------------------------------------
# Activation tests
# ---------------------------------------------------------------------------


def test_valid_staged_dataset_can_activate(clean_invoice_staging):
    """A valid staged dataset should activate successfully."""
    result = activate_staged_dataset("invoices")

    assert result["dataset"] == "invoices"
    assert result["validation"]["errors"] == 0
    assert result["validation"]["activation_allowed"] is True
    assert result["storage"] == "active"
    assert result["status"] == "activated"
    assert (DATA_DIR / "invoices.csv").exists()


def test_missing_required_column_blocks_activation(
    clean_invoice_staging,
):
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


def test_activation_consumes_staged_file(
    clean_invoice_staging,
):
    """Successful activation moves the staged file into active storage."""
    staging_path = clean_invoice_staging

    result = activate_staged_dataset("invoices")

    assert result["status"] == "activated"
    assert not staging_path.exists()
    assert (DATA_DIR / "invoices.csv").exists()


# ---------------------------------------------------------------------------
# Upload tests
# ---------------------------------------------------------------------------


class FakeUploadedFile:
    """Minimal upload object compatible with save_uploaded_dataset."""

    def __init__(self, content: bytes):
        self.file = self
        self._content = content

    def read(self):
        content = self._content
        self._content = b""
        return content


def test_save_uploaded_dataset_stores_file_in_staging():
    staging_path = STAGING_DIR / "invoices.csv"

    original = (
        staging_path.read_bytes()
        if staging_path.exists()
        else None
    )

    try:
        content = (
            b"invoice_id,customer,invoice_date,due_date,amount,currency\n"
            b"TEST-INV-001,Test Customer,2026-01-01,2026-02-01,1000,INR\n"
        )

        result = save_uploaded_dataset(
            "invoices",
            FakeUploadedFile(content),
        )

        assert result["dataset"] == "invoices"
        assert result["filename"] == "invoices.csv"
        assert result["storage"] == "staging"
        assert result["size_bytes"] == len(content)
        assert result["validation"]["rows"] == 1
        assert result["validation"]["columns"] == 6
        assert staging_path.read_bytes() == content
    finally:
        if original is not None:
            staging_path.write_bytes(original)
        elif staging_path.exists():
            staging_path.unlink()


def test_save_uploaded_dataset_normalizes_dataset_name():
    staging_path = STAGING_DIR / "invoices.csv"

    original = (
        staging_path.read_bytes()
        if staging_path.exists()
        else None
    )

    try:
        content = (
            b"invoice_id,customer,invoice_date,due_date,amount,currency\n"
            b"TEST-INV-002,Test Customer,2026-01-01,2026-02-01,2000,INR\n"
        )

        result = save_uploaded_dataset(
            "  INVOICES  ",
            FakeUploadedFile(content),
        )

        assert result["dataset"] == "invoices"
        assert result["storage"] == "staging"
    finally:
        if original is not None:
            staging_path.write_bytes(original)
        elif staging_path.exists():
            staging_path.unlink()


def test_save_uploaded_dataset_rejects_empty_file():
    staging_path = STAGING_DIR / "invoices.csv"

    original = (
        staging_path.read_bytes()
        if staging_path.exists()
        else None
    )

    try:
        with pytest.raises(
            ValueError,
            match="Uploaded file is empty",
        ):
            save_uploaded_dataset(
                "invoices",
                FakeUploadedFile(b""),
            )
    finally:
        if original is not None:
            staging_path.write_bytes(original)
        elif staging_path.exists():
            staging_path.unlink()


def test_save_uploaded_dataset_rejects_invalid_csv():
    staging_path = STAGING_DIR / "invoices.csv"

    original = (
        staging_path.read_bytes()
        if staging_path.exists()
        else None
    )

    try:
        with pytest.raises(
            ValueError,
            match="Uploaded file is not a valid CSV",
        ):
            save_uploaded_dataset(
                "invoices",
                FakeUploadedFile(b'"broken,row\n'),
            )

        assert not staging_path.exists()
    finally:
        if original is not None:
            staging_path.write_bytes(original)
        elif staging_path.exists():
            staging_path.unlink()


def test_save_uploaded_dataset_does_not_modify_active_dataset():
    active_path = DATA_DIR / "invoices.csv"
    staging_path = STAGING_DIR / "invoices.csv"

    original_active = active_path.read_bytes()
    original_staging = (
        staging_path.read_bytes()
        if staging_path.exists()
        else None
    )

    try:
        content = (
            b"invoice_id,customer,invoice_date,due_date,amount,currency\n"
            b"TEST-INV-003,Uploaded Customer,2026-01-01,2026-02-01,3000,INR\n"
        )

        save_uploaded_dataset(
            "invoices",
            FakeUploadedFile(content),
        )

        assert active_path.read_bytes() == original_active
    finally:
        if original_staging is not None:
            staging_path.write_bytes(original_staging)
        elif staging_path.exists():
            staging_path.unlink()


# ---------------------------------------------------------------------------
# Ingestion status / active quality / import
# ---------------------------------------------------------------------------


def test_get_ingestion_status_reports_all_supported_datasets():
    result = get_ingestion_status()

    assert "datasets" in result
    assert set(result["datasets"].keys()) == {
        "invoices",
        "payments",
        "bank_transactions",
    }

    for dataset in result["datasets"].values():
        assert "filename" in dataset
        assert "active" in dataset
        assert "staging" in dataset

        assert "exists" in dataset["active"]
        assert "path" in dataset["active"]
        assert "size_bytes" in dataset["active"]

        assert "exists" in dataset["staging"]
        assert "path" in dataset["staging"]
        assert "size_bytes" in dataset["staging"]


def test_get_ingestion_status_reports_existing_active_files():
    result = get_ingestion_status()

    for dataset in result["datasets"].values():
        assert dataset["active"]["exists"] is True
        assert dataset["active"]["size_bytes"] > 0


def test_run_ingestion_quality_check_returns_quality_summary():
    result = run_ingestion_quality_check()

    assert "quality_score" in result
    assert "total_records" in result
    assert "valid_records" in result
    assert "warnings" in result
    assert "errors" in result


def test_source_import_only_updates_source_datasets():
    """Phase 10 import must only import the three source datasets."""
    result = import_active_datasets()

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