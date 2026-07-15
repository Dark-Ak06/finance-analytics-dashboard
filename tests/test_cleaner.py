"""Tests for src/cleaner.py"""

import sys
from pathlib import Path

import pandas as pd
import pytest

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

from cleaner import clean_transactions  # noqa: E402


@pytest.fixture
def messy_df() -> pd.DataFrame:
    return pd.DataFrame({
        "Date": ["2026-01-01", "2026-01-01", "2026-01-02", None, "not-a-date"],
        "Type": ["Income", "Income", "Expense", None, "Expense"],
        "Category": ["Salary", "Salary", "Food", None, "Transport"],
        "Description": ["Salary", "Salary", "Lunch", None, "Taxi"],
        "Amount": [450000, 450000, -3500, None, 1200],
        "Payment Method": ["Bank", "Bank", "Card", None, "Cash"],
        "Month": ["January", "January", "January", None, "January"],
    })


def test_clean_removes_duplicates(messy_df: pd.DataFrame) -> None:
    cleaned = clean_transactions(messy_df)
    # The two identical Salary rows should collapse to one.
    salary_rows = cleaned[cleaned["Category"] == "Salary"]
    assert len(salary_rows) == 1


def test_clean_removes_fully_empty_rows(messy_df: pd.DataFrame) -> None:
    cleaned = clean_transactions(messy_df)
    assert cleaned.isna().all(axis=1).sum() == 0


def test_clean_fixes_negative_amounts(messy_df: pd.DataFrame) -> None:
    cleaned = clean_transactions(messy_df)
    assert (cleaned["Amount"] >= 0).all()


def test_clean_drops_unparsable_dates(messy_df: pd.DataFrame) -> None:
    cleaned = clean_transactions(messy_df)
    assert cleaned["Date"].isna().sum() == 0


def test_clean_returns_dataframe_with_reset_index(messy_df: pd.DataFrame) -> None:
    cleaned = clean_transactions(messy_df)
    assert list(cleaned.index) == list(range(len(cleaned)))


def test_clean_recomputes_month_from_date() -> None:
    df = pd.DataFrame({
        "Date": ["2026-03-15"],
        "Type": ["Expense"],
        "Category": ["Food"],
        "Description": ["Dinner"],
        "Amount": [5000],
        "Payment Method": ["Card"],
        "Month": ["WrongMonth"],
    })
    cleaned = clean_transactions(df)
    assert cleaned.loc[0, "Month"] == "March"
