"""
analyzer.py

Performs all financial analytics on cleaned transaction data: overall
KPIs, category breakdowns, monthly trends, and payment-method analysis.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import pandas as pd

logger = logging.getLogger(__name__)

MONTH_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


@dataclass
class OverallStats:
    """Top-level financial KPIs."""
    total_income: float
    total_expense: float
    net_profit: float
    average_expense: float
    average_income: float
    max_expense: float
    max_income: float
    min_expense: float
    min_income: float
    total_transactions: int
    total_expense_count: int
    total_income_count: int


@dataclass
class CategoryStats:
    """Category-level breakdown of income and expenses."""
    top_expense_categories: pd.Series
    top_income_categories: pd.Series
    expense_category_percent: pd.Series
    income_category_percent: pd.Series
    most_expensive_category: str
    most_profitable_category: str


@dataclass
class MonthlyStats:
    """Month-by-month income, expense, profit and growth rates."""
    monthly_income: pd.Series
    monthly_expense: pd.Series
    monthly_profit: pd.Series
    expense_growth_rate: pd.Series
    income_growth_rate: pd.Series


@dataclass
class PaymentStats:
    """Breakdown of activity by payment method."""
    most_used_method: str
    totals_by_method: pd.Series
    counts_by_method: pd.Series


@dataclass
class AnalysisResult:
    """Container bundling every analysis result together."""
    overall: OverallStats
    categories: CategoryStats
    monthly: MonthlyStats
    payments: PaymentStats


def _reindex_by_month_order(series: pd.Series) -> pd.Series:
    """Reindex a series whose index is month names into calendar order."""
    ordered_index = [m for m in MONTH_ORDER if m in series.index]
    return series.reindex(ordered_index)


def compute_overall_stats(df: pd.DataFrame) -> OverallStats:
    """Compute top-level KPIs across all transactions."""
    expenses = df.loc[df["Type"] == "Expense", "Amount"]
    incomes = df.loc[df["Type"] == "Income", "Amount"]

    stats = OverallStats(
        total_income=float(incomes.sum()),
        total_expense=float(expenses.sum()),
        net_profit=float(incomes.sum() - expenses.sum()),
        average_expense=float(expenses.mean()) if not expenses.empty else 0.0,
        average_income=float(incomes.mean()) if not incomes.empty else 0.0,
        max_expense=float(expenses.max()) if not expenses.empty else 0.0,
        max_income=float(incomes.max()) if not incomes.empty else 0.0,
        min_expense=float(expenses.min()) if not expenses.empty else 0.0,
        min_income=float(incomes.min()) if not incomes.empty else 0.0,
        total_transactions=int(len(df)),
        total_expense_count=int(len(expenses)),
        total_income_count=int(len(incomes)),
    )
    logger.info("Computed overall stats: net_profit=%.2f", stats.net_profit)
    return stats


def compute_category_stats(df: pd.DataFrame) -> CategoryStats:
    """Compute top categories and their share of income/expense totals."""
    expenses = df[df["Type"] == "Expense"]
    incomes = df[df["Type"] == "Income"]

    expense_by_category = expenses.groupby("Category")["Amount"].sum().sort_values(ascending=False)
    income_by_category = incomes.groupby("Category")["Amount"].sum().sort_values(ascending=False)

    total_expense = expense_by_category.sum()
    total_income = income_by_category.sum()

    expense_percent = (expense_by_category / total_expense * 100) if total_expense else expense_by_category
    income_percent = (income_by_category / total_income * 100) if total_income else income_by_category

    stats = CategoryStats(
        top_expense_categories=expense_by_category.head(10),
        top_income_categories=income_by_category.head(10),
        expense_category_percent=expense_percent,
        income_category_percent=income_percent,
        most_expensive_category=str(expense_by_category.idxmax()) if not expense_by_category.empty else "N/A",
        most_profitable_category=str(income_by_category.idxmax()) if not income_by_category.empty else "N/A",
    )
    logger.info("Most expensive category: %s", stats.most_expensive_category)
    return stats


def compute_monthly_stats(df: pd.DataFrame) -> MonthlyStats:
    """Compute income/expense/profit per month and month-over-month growth."""
    expenses = df[df["Type"] == "Expense"]
    incomes = df[df["Type"] == "Income"]

    monthly_expense = _reindex_by_month_order(expenses.groupby("Month")["Amount"].sum()).fillna(0)
    monthly_income = _reindex_by_month_order(incomes.groupby("Month")["Amount"].sum()).fillna(0)
    monthly_profit = monthly_income - monthly_expense

    expense_growth = monthly_expense.pct_change().fillna(0) * 100
    income_growth = monthly_income.pct_change().fillna(0) * 100

    stats = MonthlyStats(
        monthly_income=monthly_income,
        monthly_expense=monthly_expense,
        monthly_profit=monthly_profit,
        expense_growth_rate=expense_growth,
        income_growth_rate=income_growth,
    )
    logger.info("Computed monthly stats for %d month(s)", len(monthly_expense))
    return stats


def compute_payment_stats(df: pd.DataFrame) -> PaymentStats:
    """Compute totals and usage counts by payment method."""
    counts = df["Payment Method"].value_counts()
    totals = df.groupby("Payment Method")["Amount"].sum().sort_values(ascending=False)

    stats = PaymentStats(
        most_used_method=str(counts.idxmax()) if not counts.empty else "N/A",
        totals_by_method=totals,
        counts_by_method=counts,
    )
    logger.info("Most used payment method: %s", stats.most_used_method)
    return stats


def run_full_analysis(df: pd.DataFrame) -> AnalysisResult:
    """Run every analysis step and bundle the results together."""
    logger.info("Running full analysis on %d transactions", len(df))
    return AnalysisResult(
        overall=compute_overall_stats(df),
        categories=compute_category_stats(df),
        monthly=compute_monthly_stats(df),
        payments=compute_payment_stats(df),
    )
