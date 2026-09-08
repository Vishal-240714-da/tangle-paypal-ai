import pandas as pd

from backend.services.data_quality_service import (
    _validate_dataframe_structure,
    _validate_amounts,
    _validate_dates,
    _validate_currencies,
)


def test_duplicate_records():
    df = pd.DataFrame(
        {
            "invoice_id": [
                "INV-001",
                "INV-001",
            ],
            "amount": [
                1000,
                2000,
            ],
        }
    )

    issues = _validate_dataframe_structure(
        df=df,
        dataset="test",
        required_columns=[
            "invoice_id",
            "amount",
        ],
        id_column="invoice_id",
    )

    assert any(
        issue.issue_type == "DUPLICATE_RECORD"
        for issue in issues
    )


def test_missing_id():
    df = pd.DataFrame(
        {
            "invoice_id": [
                None,
            ],
            "amount": [
                1000,
            ],
        }
    )

    issues = _validate_dataframe_structure(
        df=df,
        dataset="test",
        required_columns=[
            "invoice_id",
            "amount",
        ],
        id_column="invoice_id",
    )

    assert any(
        issue.issue_type == "MISSING_ID"
        for issue in issues
    )


def test_invalid_amount():
    df = pd.DataFrame(
        {
            "invoice_id": [
                "INV-001",
            ],
            "amount": [
                "ABC",
            ],
        }
    )

    issues = _validate_amounts(
        df=df,
        dataset="test",
        id_column="invoice_id",
        amount_columns=[
            "amount",
        ],
    )

    assert any(
        issue.issue_type == "INVALID_AMOUNT"
        for issue in issues
    )


def test_negative_value():
    df = pd.DataFrame(
        {
            "invoice_id": [
                "INV-001",
            ],
            "amount": [
                -500,
            ],
        }
    )

    issues = _validate_amounts(
        df=df,
        dataset="test",
        id_column="invoice_id",
        amount_columns=[
            "amount",
        ],
    )

    assert any(
        issue.issue_type == "NEGATIVE_VALUE"
        for issue in issues
    )


def test_invalid_date():
    df = pd.DataFrame(
        {
            "invoice_id": [
                "INV-001",
            ],
            "invoice_date": [
                "not-a-date",
            ],
        }
    )

    issues = _validate_dates(
        df=df,
        dataset="test",
        id_column="invoice_id",
        date_columns=[
            "invoice_date",
        ],
    )

    assert any(
        issue.issue_type == "INVALID_DATE"
        for issue in issues
    )


def test_currency_problem():
    df = pd.DataFrame(
        {
            "invoice_id": [
                "INV-001",
            ],
            "currency": [
                "XYZ",
            ],
        }
    )

    issues = _validate_currencies(
        df=df,
        dataset="test",
        id_column="invoice_id",
    )

    assert any(
        issue.issue_type == "CURRENCY_PROBLEM"
        for issue in issues
    )


def test_malformed_record():
    df = pd.DataFrame(
        {
            "invoice_id": [
                "INV-001",
            ],
        }
    )

    issues = _validate_dataframe_structure(
        df=df,
        dataset="test",
        required_columns=[
            "invoice_id",
            "amount",
            "currency",
        ],
        id_column="invoice_id",
    )

    assert any(
        issue.issue_type == "MALFORMED_RECORD"
        for issue in issues
    )


if __name__ == "__main__":
    test_duplicate_records()
    test_missing_id()
    test_invalid_amount()
    test_negative_value()
    test_invalid_date()
    test_currency_problem()
    test_malformed_record()

    print("All Data Quality tests passed!")