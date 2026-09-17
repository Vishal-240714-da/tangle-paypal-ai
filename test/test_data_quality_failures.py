from pathlib import Path

import pandas as pd
import pytest

from backend.services.data_quality_service import (
    _is_missing,
    _record_id,
    _validate_dataframe_structure,
    _validate_amounts,
    _validate_dates,
    _validate_currencies,
    _validate_relationships,
    _load_datasets,
    run_data_quality_check,
    run_staged_data_quality_check,
)


def test_is_missing_handles_none_nan_and_blank_values():
    assert _is_missing(None) is True
    assert _is_missing(float("nan")) is True
    assert _is_missing("") is True
    assert _is_missing("   ") is True
    assert _is_missing("value") is False
    assert _is_missing(0) is False


def test_record_id_normalizes_values():
    assert _record_id(None) is None
    assert _record_id("") is None
    assert _record_id("   ") is None
    assert _record_id(" INV-001 ") == "INV-001"
    assert _record_id(12345) == "12345"


def test_structure_validation_detects_missing_columns():
    df = pd.DataFrame(
        {
            "invoice_id": ["INV-001"],
            "amount": [1000],
        }
    )

    issues = _validate_dataframe_structure(
        df=df,
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
    )

    assert len(issues) == 1
    assert issues[0].issue_type == "MALFORMED_RECORD"
    assert issues[0].severity == "ERROR"
    assert "customer" in issues[0].message
    assert "currency" in issues[0].message


def test_structure_validation_detects_missing_ids():
    df = pd.DataFrame(
        {
            "invoice_id": ["INV-001", None, ""],
            "amount": [100, 200, 300],
        }
    )

    issues = _validate_dataframe_structure(
        df=df,
        dataset="invoices",
        required_columns=["invoice_id", "amount"],
        id_column="invoice_id",
    )

    missing_id_issues = [
        issue
        for issue in issues
        if issue.issue_type == "MISSING_ID"
    ]

    assert len(missing_id_issues) == 2
    assert all(issue.severity == "ERROR" for issue in missing_id_issues)


def test_structure_validation_detects_duplicate_ids():
    df = pd.DataFrame(
        {
            "invoice_id": [
                "INV-001",
                "INV-001",
                "INV-002",
            ],
            "amount": [100, 200, 300],
        }
    )

    issues = _validate_dataframe_structure(
        df=df,
        dataset="invoices",
        required_columns=["invoice_id", "amount"],
        id_column="invoice_id",
    )

    duplicate_issues = [
        issue
        for issue in issues
        if issue.issue_type == "DUPLICATE_RECORD"
    ]

    assert len(duplicate_issues) == 2
    assert all(issue.record_id == "INV-001" for issue in duplicate_issues)


def test_amount_validation_detects_missing_non_numeric_and_negative():
    df = pd.DataFrame(
        {
            "invoice_id": [
                "INV-MISSING",
                "INV-TEXT",
                "INV-NEGATIVE",
                "INV-VALID",
            ],
            "amount": [
                None,
                "abc",
                -100,
                500,
            ],
        }
    )

    issues = _validate_amounts(
        df=df,
        dataset="invoices",
        id_column="invoice_id",
        amount_columns=["amount"],
    )

    assert len(issues) == 3

    issue_types = [issue.issue_type for issue in issues]

    assert issue_types.count("INVALID_AMOUNT") == 2
    assert issue_types.count("NEGATIVE_VALUE") == 1


def test_amount_validation_skips_missing_amount_column():
    df = pd.DataFrame(
        {
            "invoice_id": ["INV-001"],
        }
    )

    issues = _validate_amounts(
        df=df,
        dataset="invoices",
        id_column="invoice_id",
        amount_columns=["amount"],
    )

    assert issues == []


def test_date_validation_detects_missing_and_invalid_dates():
    df = pd.DataFrame(
        {
            "invoice_id": [
                "INV-MISSING",
                "INV-INVALID",
                "INV-VALID",
            ],
            "invoice_date": [
                None,
                "not-a-date",
                "2026-01-15",
            ],
        }
    )

    issues = _validate_dates(
        df=df,
        dataset="invoices",
        id_column="invoice_id",
        date_columns=["invoice_date"],
    )

    assert len(issues) == 2
    assert all(issue.issue_type == "INVALID_DATE" for issue in issues)
    assert all(issue.severity == "ERROR" for issue in issues)


def test_currency_validation_detects_missing_and_unsupported_currency():
    df = pd.DataFrame(
        {
            "invoice_id": [
                "INV-MISSING",
                "INV-UNSUPPORTED",
                "INV-VALID",
            ],
            "currency": [
                None,
                "JPY",
                "INR",
            ],
        }
    )

    issues = _validate_currencies(
        df=df,
        dataset="invoices",
        id_column="invoice_id",
    )

    assert len(issues) == 2

    assert all(
        issue.issue_type == "CURRENCY_PROBLEM"
        for issue in issues
    )

    assert all(
        issue.severity == "WARNING"
        for issue in issues
    )


def test_currency_validation_accepts_supported_currencies():
    df = pd.DataFrame(
        {
            "invoice_id": [
                "INV-INR",
                "INV-USD",
                "INV-EUR",
                "INV-GBP",
            ],
            "currency": [
                "INR",
                "USD",
                "EUR",
                "GBP",
            ],
        }
    )

    issues = _validate_currencies(
        df=df,
        dataset="invoices",
        id_column="invoice_id",
    )

    assert issues == []


def test_relationship_validation_detects_missing_invoice_reference():
    invoices = pd.DataFrame(
        {
            "invoice_id": ["INV-001"],
        }
    )

    payments = pd.DataFrame(
        {
            "payment_id": ["PAY-001"],
            "invoice_reference": [None],
        }
    )

    banks = pd.DataFrame(
        {
            "bank_transaction_id": ["BANK-001"],
            "gateway_reference": ["PAY-001"],
        }
    )

    issues = _validate_relationships(
        invoices=invoices,
        payments=payments,
        bank_transactions=banks,
    )

    matching = [
        issue
        for issue in issues
        if issue.record_id == "PAY-001"
        and issue.issue_type == "MISSING_RELATIONSHIP"
    ]

    assert len(matching) >= 1
    assert any(
        "invoice reference" in issue.message.lower()
        for issue in matching
    )


def test_relationship_validation_detects_unknown_invoice_reference():
    invoices = pd.DataFrame(
        {
            "invoice_id": ["INV-001"],
        }
    )

    payments = pd.DataFrame(
        {
            "payment_id": ["PAY-001"],
            "invoice_reference": ["INV-UNKNOWN"],
        }
    )

    banks = pd.DataFrame(
        {
            "bank_transaction_id": ["BANK-001"],
            "gateway_reference": ["PAY-001"],
        }
    )

    issues = _validate_relationships(
        invoices=invoices,
        payments=payments,
        bank_transactions=banks,
    )

    assert any(
        issue.issue_type == "MISSING_RELATIONSHIP"
        and issue.record_id == "PAY-001"
        and "INV-UNKNOWN" in issue.message
        for issue in issues
    )


def test_relationship_validation_detects_unknown_payment_reference():
    invoices = pd.DataFrame(
        {
            "invoice_id": ["INV-001"],
        }
    )

    payments = pd.DataFrame(
        {
            "payment_id": ["PAY-001"],
            "invoice_reference": ["INV-001"],
        }
    )

    banks = pd.DataFrame(
        {
            "bank_transaction_id": ["BANK-001"],
            "gateway_reference": ["PAY-UNKNOWN"],
        }
    )

    issues = _validate_relationships(
        invoices=invoices,
        payments=payments,
        bank_transactions=banks,
    )

    assert any(
        issue.issue_type == "MISSING_RELATIONSHIP"
        and issue.record_id == "BANK-001"
        and "PAY-UNKNOWN" in issue.message
        for issue in issues
    )


def test_relationship_validation_detects_payment_without_bank_transaction():
    invoices = pd.DataFrame(
        {
            "invoice_id": ["INV-001"],
        }
    )

    payments = pd.DataFrame(
        {
            "payment_id": ["PAY-001"],
            "invoice_reference": ["INV-001"],
        }
    )

    banks = pd.DataFrame(
        {
            "bank_transaction_id": [],
            "gateway_reference": [],
        }
    )

    issues = _validate_relationships(
        invoices=invoices,
        payments=payments,
        bank_transactions=banks,
    )

    assert any(
        issue.issue_type == "MISSING_RELATIONSHIP"
        and issue.record_id == "PAY-001"
        and "bank transaction" in issue.message.lower()
        for issue in issues
    )


def test_relationship_validation_supports_multi_invoice_payment():
    invoices = pd.DataFrame(
        {
            "invoice_id": [
                "INV-001",
                "INV-002",
            ],
        }
    )

    payments = pd.DataFrame(
        {
            "payment_id": ["PAY-001"],
            "invoice_reference": ["INV-001|INV-002"],
        }
    )

    banks = pd.DataFrame(
        {
            "bank_transaction_id": ["BANK-001"],
            "gateway_reference": ["PAY-001"],
        }
    )

    issues = _validate_relationships(
        invoices=invoices,
        payments=payments,
        bank_transactions=banks,
    )

    assert issues == []


def test_load_datasets_raises_when_directory_is_missing(tmp_path):
    missing_directory = tmp_path / "missing_data"

    with pytest.raises(FileNotFoundError) as exc_info:
        _load_datasets(missing_directory)

    assert "invoices.csv" in str(exc_info.value)
    assert "payments.csv" in str(exc_info.value)
    assert "bank_transactions.csv" in str(exc_info.value)


def test_load_datasets_raises_when_one_required_file_is_missing(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    pd.DataFrame(
        {
            "invoice_id": ["INV-001"],
            "amount": [100],
        }
    ).to_csv(data_dir / "invoices.csv", index=False)

    pd.DataFrame(
        {
            "payment_id": ["PAY-001"],
            "amount": [100],
        }
    ).to_csv(data_dir / "payments.csv", index=False)

    with pytest.raises(FileNotFoundError) as exc_info:
        _load_datasets(data_dir)

    assert "bank_transactions.csv" in str(exc_info.value)


def test_run_data_quality_check_returns_expected_structure():
    result = run_data_quality_check()

    assert isinstance(result, dict)

    assert "quality_score" in result
    assert "total_records" in result
    assert "valid_records" in result
    assert "warnings" in result
    assert "errors" in result
    assert "datasets" in result
    assert "issue_summary" in result
    assert "issues" in result

    assert isinstance(result["quality_score"], float)
    assert result["total_records"] >= 0
    assert result["valid_records"] >= 0
    assert result["warnings"] >= 0
    assert result["errors"] >= 0
    assert isinstance(result["issues"], list)


def test_run_data_quality_check_on_empty_datasets():
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as temporary_directory:
        data_dir = Path(temporary_directory)

        pd.DataFrame(
            columns=[
                "invoice_id",
                "customer",
                "invoice_date",
                "due_date",
                "amount",
                "currency",
            ]
        ).to_csv(data_dir / "invoices.csv", index=False)

        pd.DataFrame(
            columns=[
                "payment_id",
                "invoice_reference",
                "customer",
                "payment_date",
                "amount",
                "currency",
                "fee",
                "original_invoice_amount",
            ]
        ).to_csv(data_dir / "payments.csv", index=False)

        pd.DataFrame(
            columns=[
                "bank_transaction_id",
                "deposit_date",
                "amount",
                "currency",
                "gateway_reference",
            ]
        ).to_csv(data_dir / "bank_transactions.csv", index=False)

        result = run_data_quality_check(data_dir)

        assert result["total_records"] == 0
        assert result["valid_records"] == 0
        assert result["quality_score"] == 100.0
        assert result["errors"] == 0
        assert result["warnings"] == 0
        assert result["issues"] == []


def test_staged_quality_check_rejects_unsupported_dataset():
    with pytest.raises(ValueError) as exc_info:
        run_staged_data_quality_check("customers")

    assert "Unsupported dataset" in str(exc_info.value)


def test_staged_quality_check_normalizes_dataset_name_before_validation():
    with pytest.raises(ValueError) as exc_info:
        run_staged_data_quality_check("  CUSTOMERS  ")

    assert "Unsupported dataset" in str(exc_info.value)