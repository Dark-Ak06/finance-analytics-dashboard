"""Tests for src/web_export.py"""

import json
import sys
from pathlib import Path

import pandas as pd
import pytest

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

from analyzer import run_full_analysis  # noqa: E402
from web_export import build_dashboard_payload, export_dashboard_json  # noqa: E402


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


def test_build_dashboard_payload_has_expected_keys(sample_df: pd.DataFrame) -> None:
    analysis = run_full_analysis(sample_df)
    payload = build_dashboard_payload(sample_df, analysis)
    for key in ["overall", "categories", "monthly", "payments", "category_month_matrix", "transactions"]:
        assert key in payload


def test_build_dashboard_payload_transaction_count_matches(sample_df: pd.DataFrame) -> None:
    analysis = run_full_analysis(sample_df)
    payload = build_dashboard_payload(sample_df, analysis)
    assert len(payload["transactions"]) == len(sample_df)


def test_export_dashboard_json_creates_valid_json(tmp_path: Path, sample_df: pd.DataFrame) -> None:
    analysis = run_full_analysis(sample_df)
    output_path = tmp_path / "dashboard_data.json"
    result_path = export_dashboard_json(sample_df, analysis, output_path)

    assert result_path.exists()
    with result_path.open(encoding="utf-8") as f:
        data = json.load(f)
    assert data["overall"]["total_transactions"] == len(sample_df)


def test_export_dashboard_json_is_json_serializable(tmp_path: Path, sample_df: pd.DataFrame) -> None:
    """Every value in the payload must survive a JSON round-trip without errors."""
    analysis = run_full_analysis(sample_df)
    output_path = tmp_path / "dashboard_data.json"
    export_dashboard_json(sample_df, analysis, output_path)

    with output_path.open(encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data["monthly"]["months"], list)
    assert isinstance(data["category_month_matrix"]["values"], list)
