"""Tests for src/generate_sample_data.py"""

import sys
from pathlib import Path

import pytest

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

from generate_sample_data import (  # noqa: E402
    EXPENSE_CATEGORIES,
    INCOME_CATEGORIES,
    generate_transactions,
    save_sample_data,
)


def test_generate_transactions_returns_requested_row_count() -> None:
    df = generate_transactions(number_of_records=100)
    # A few extra rows are injected intentionally (duplicate/negative/blank).
    assert len(df) >= 100


def test_generate_transactions_has_expected_columns() -> None:
    df = generate_transactions(number_of_records=50)
    for column in ["Date", "Type", "Category", "Description", "Amount", "Payment Method", "Month"]:
        assert column in df.columns


def test_generate_transactions_types_are_valid() -> None:
    df = generate_transactions(number_of_records=50)
    valid_types = {"Income", "Expense", None}
    assert set(df["Type"].dropna().unique()).issubset({"Income", "Expense"})


def test_generate_transactions_categories_are_known() -> None:
    df = generate_transactions(number_of_records=200)
    known_categories = set(EXPENSE_CATEGORIES) | set(INCOME_CATEGORIES)
    actual_categories = set(df["Category"].dropna().unique())
    assert actual_categories.issubset(known_categories)


def test_save_sample_data_creates_file(tmp_path: Path) -> None:
    output_path = tmp_path / "sample.xlsx"
    result_path = save_sample_data(output_path)
    assert result_path.exists()
    assert result_path.suffix == ".xlsx"
