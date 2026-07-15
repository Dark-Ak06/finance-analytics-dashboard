"""Tests for src/loader.py"""

import sys
from pathlib import Path

import pandas as pd
import pytest

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

from loader import DataLoadError, load_transactions  # noqa: E402


@pytest.fixture
def valid_excel_file(tmp_path: Path) -> Path:
    df = pd.DataFrame({
        "Date": ["2026-01-01", "2026-01-02"],
        "Type": ["Income", "Expense"],
        "Category": ["Salary", "Food"],
        "Description": ["January salary", "Lunch"],
        "Amount": [450000, 3500],
        "Payment Method": ["Bank", "Card"],
        "Month": ["January", "January"],
    })
    file_path = tmp_path / "transactions.xlsx"
    df.to_excel(file_path, index=False, sheet_name="Transactions")
    return file_path


def test_load_transactions_returns_dataframe(valid_excel_file: Path) -> None:
    df = load_transactions(valid_excel_file)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2


def test_load_transactions_has_expected_columns(valid_excel_file: Path) -> None:
    df = load_transactions(valid_excel_file)
    for column in ["Date", "Type", "Category", "Description", "Amount", "Payment Method", "Month"]:
        assert column in df.columns


def test_load_transactions_missing_file_raises(tmp_path: Path) -> None:
    missing_path = tmp_path / "does_not_exist.xlsx"
    with pytest.raises(DataLoadError):
        load_transactions(missing_path)


def test_load_transactions_missing_columns_raises(tmp_path: Path) -> None:
    df = pd.DataFrame({"Date": ["2026-01-01"], "Amount": [100]})
    file_path = tmp_path / "bad.xlsx"
    df.to_excel(file_path, index=False, sheet_name="Transactions")
    with pytest.raises(DataLoadError):
        load_transactions(file_path)
