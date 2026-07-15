"""
web_export.py

Exports the cleaned transactions and full analysis results to a single
JSON file consumed by the static interactive dashboard in docs/.
This lets the dashboard run entirely client-side (GitHub Pages, no
backend) while staying in sync with the Python analytics pipeline.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pandas as pd

from analyzer import AnalysisResult

logger = logging.getLogger(__name__)


def _series_to_records(series: pd.Series, key_name: str, value_name: str) -> list[dict]:
    return [{key_name: str(idx), value_name: (float(val) if pd.notna(val) else 0.0)}
            for idx, val in series.items()]


def _transactions_to_records(df: pd.DataFrame) -> list[dict]:
    records = []
    for _, row in df.iterrows():
        records.append({
            "date": row["Date"].strftime("%Y-%m-%d") if pd.notna(row["Date"]) else None,
            "type": row["Type"],
            "category": row["Category"],
            "description": row["Description"],
            "amount": float(row["Amount"]),
            "payment_method": row["Payment Method"],
            "month": row["Month"],
        })
    return records


def build_dashboard_payload(df: pd.DataFrame, analysis: AnalysisResult) -> dict:
    """Assemble the full JSON-serializable payload for the web dashboard."""
    overall = analysis.overall
    categories = analysis.categories
    monthly = analysis.monthly
    payments = analysis.payments

    payload = {
        "generated_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
        "overall": {
            "total_income": overall.total_income,
            "total_expense": overall.total_expense,
            "net_profit": overall.net_profit,
            "average_expense": overall.average_expense,
            "average_income": overall.average_income,
            "max_expense": overall.max_expense,
            "max_income": overall.max_income,
            "min_expense": overall.min_expense,
            "min_income": overall.min_income,
            "total_transactions": overall.total_transactions,
            "total_expense_count": overall.total_expense_count,
            "total_income_count": overall.total_income_count,
        },
        "categories": {
            "top_expense": _series_to_records(categories.top_expense_categories, "category", "amount"),
            "top_income": _series_to_records(categories.top_income_categories, "category", "amount"),
            "expense_percent": _series_to_records(categories.expense_category_percent, "category", "percent"),
            "income_percent": _series_to_records(categories.income_category_percent, "category", "percent"),
            "most_expensive_category": categories.most_expensive_category,
            "most_profitable_category": categories.most_profitable_category,
        },
        "monthly": {
            "months": list(monthly.monthly_income.index),
            "income": [float(v) for v in monthly.monthly_income.values],
            "expense": [float(v) for v in monthly.monthly_expense.values],
            "profit": [float(v) for v in monthly.monthly_profit.values],
            "income_growth": [float(v) for v in monthly.income_growth_rate.values],
            "expense_growth": [float(v) for v in monthly.expense_growth_rate.values],
        },
        "payments": {
            "most_used_method": payments.most_used_method,
            "totals_by_method": _series_to_records(payments.totals_by_method, "method", "amount"),
            "counts_by_method": _series_to_records(payments.counts_by_method, "method", "count"),
        },
        "category_month_matrix": _build_category_month_matrix(df),
        "transactions": _transactions_to_records(df),
    }
    return payload


def _build_category_month_matrix(df: pd.DataFrame) -> dict:
    from analyzer import MONTH_ORDER

    expenses = df[df["Type"] == "Expense"]
    pivot = expenses.pivot_table(
        index="Category", columns="Month", values="Amount", aggfunc="sum", fill_value=0
    )
    ordered_columns = [m for m in MONTH_ORDER if m in pivot.columns]
    pivot = pivot[ordered_columns]

    return {
        "categories": list(pivot.index),
        "months": list(pivot.columns),
        "values": pivot.values.tolist(),
    }


def export_dashboard_json(df: pd.DataFrame, analysis: AnalysisResult, output_path: Path) -> Path:
    """Build the dashboard payload and write it to output_path as JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_dashboard_payload(df, analysis)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    logger.info("Dashboard JSON exported to %s", output_path)
    return output_path
