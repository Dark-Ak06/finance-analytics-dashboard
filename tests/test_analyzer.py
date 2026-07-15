"""Tests for src/analyzer.py"""

import sys
from pathlib import Path

import pandas as pd
import pytest

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

from analyzer import (  # noqa: E402
    compute_category_stats,
    compute_monthly_stats,
    compute_overall_stats,
    compute_payment_stats,
    run_full_analysis,
)


@pytest.fixture
def sample_df() -> pd.DataFrame:
    return pd.DataFrame({
        "Date": pd.to_datetime([
            "2026-01-05", "2026-01-10", "2026-02-05", "2026-02-15", "2026-02-20",
        ]),
        "Type": ["Income", "Expense", "Income", "Expense", "Expense"],
        "Category": ["Salary", "Food", "Salary", "Rent", "Food"],
        "Description": ["Salary", "Lunch", "Salary", "Rent", "Dinner"],
        "Amount": [400000, 5000, 420000, 150000, 7000],
        "Payment Method": ["Bank", "Card", "Bank", "Bank", "Cash"],
        "Month": ["January", "January", "February", "February", "February"],
    })


def test_overall_stats_totals(sample_df: pd.DataFrame) -> None:
    stats = compute_overall_stats(sample_df)
    assert stats.total_income == pytest.approx(820000)
    assert stats.total_expense == pytest.approx(162000)
    assert stats.net_profit == pytest.approx(658000)


def test_overall_stats_counts(sample_df: pd.DataFrame) -> None:
    stats = compute_overall_stats(sample_df)
    assert stats.total_transactions == 5
    assert stats.total_income_count == 2
    assert stats.total_expense_count == 3


def test_category_stats_most_expensive(sample_df: pd.DataFrame) -> None:
    stats = compute_category_stats(sample_df)
    assert stats.most_expensive_category == "Rent"


def test_category_stats_percentages_sum_to_100(sample_df: pd.DataFrame) -> None:
    stats = compute_category_stats(sample_df)
    assert stats.expense_category_percent.sum() == pytest.approx(100)


def test_monthly_stats_profit(sample_df: pd.DataFrame) -> None:
    stats = compute_monthly_stats(sample_df)
    assert stats.monthly_profit["January"] == pytest.approx(395000)
    assert stats.monthly_profit["February"] == pytest.approx(263000)


def test_payment_stats_most_used(sample_df: pd.DataFrame) -> None:
    stats = compute_payment_stats(sample_df)
    assert stats.most_used_method == "Bank"


def test_run_full_analysis_returns_all_sections(sample_df: pd.DataFrame) -> None:
    result = run_full_analysis(sample_df)
    assert result.overall is not None
    assert result.categories is not None
    assert result.monthly is not None
    assert result.payments is not None
