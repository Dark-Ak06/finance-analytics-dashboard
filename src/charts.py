"""
charts.py

Generates all charts required by the project and saves them as PNG
files inside the charts/ directory.
"""

from __future__ import annotations

import logging
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless rendering, no display required

import matplotlib.pyplot as plt
import pandas as pd

from analyzer import AnalysisResult

logger = logging.getLogger(__name__)

plt.rcParams["figure.figsize"] = (10, 6)
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3

COLOR_INCOME = "#2E8B57"
COLOR_EXPENSE = "#C0392B"
CATEGORY_PALETTE = plt.get_cmap("tab20").colors


def _save(fig: plt.Figure, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    logger.info("Saved chart: %s", path)


def plot_income_line(monthly_income: pd.Series, output_dir: Path) -> Path:
    """1. Line chart of income by month."""
    fig, ax = plt.subplots()
    ax.plot(monthly_income.index, monthly_income.values, marker="o", color=COLOR_INCOME, linewidth=2)
    ax.set_title("Monthly Income")
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount")
    ax.tick_params(axis="x", rotation=45)
    path = output_dir / "01_income_line.png"
    _save(fig, path)
    return path


def plot_expense_line(monthly_expense: pd.Series, output_dir: Path) -> Path:
    """2. Line chart of expenses by month."""
    fig, ax = plt.subplots()
    ax.plot(monthly_expense.index, monthly_expense.values, marker="o", color=COLOR_EXPENSE, linewidth=2)
    ax.set_title("Monthly Expenses")
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount")
    ax.tick_params(axis="x", rotation=45)
    path = output_dir / "02_expense_line.png"
    _save(fig, path)
    return path


def plot_expense_category_pie(expense_percent: pd.Series, output_dir: Path) -> Path:
    """3. Pie chart of expense categories."""
    fig, ax = plt.subplots()
    ax.pie(
        expense_percent.values,
        labels=expense_percent.index,
        autopct="%1.1f%%",
        colors=CATEGORY_PALETTE,
        startangle=90,
    )
    ax.set_title("Expense Categories")
    path = output_dir / "03_expense_category_pie.png"
    _save(fig, path)
    return path


def plot_income_category_pie(income_percent: pd.Series, output_dir: Path) -> Path:
    """4. Pie chart of income categories."""
    fig, ax = plt.subplots()
    ax.pie(
        income_percent.values,
        labels=income_percent.index,
        autopct="%1.1f%%",
        colors=CATEGORY_PALETTE,
        startangle=90,
    )
    ax.set_title("Income Categories")
    path = output_dir / "04_income_category_pie.png"
    _save(fig, path)
    return path


def plot_expense_category_bar(top_expense_categories: pd.Series, output_dir: Path) -> Path:
    """5. Bar chart of top expense categories."""
    fig, ax = plt.subplots()
    ax.bar(top_expense_categories.index, top_expense_categories.values, color=COLOR_EXPENSE)
    ax.set_title("Top Expense Categories")
    ax.set_ylabel("Amount")
    ax.tick_params(axis="x", rotation=45)
    path = output_dir / "05_expense_category_bar.png"
    _save(fig, path)
    return path


def plot_income_category_bar(top_income_categories: pd.Series, output_dir: Path) -> Path:
    """6. Bar chart of top income categories."""
    fig, ax = plt.subplots()
    ax.bar(top_income_categories.index, top_income_categories.values, color=COLOR_INCOME)
    ax.set_title("Top Income Categories")
    ax.set_ylabel("Amount")
    ax.tick_params(axis="x", rotation=45)
    path = output_dir / "06_income_category_bar.png"
    _save(fig, path)
    return path


def plot_amount_histogram(df: pd.DataFrame, output_dir: Path) -> Path:
    """7. Histogram of all transaction amounts."""
    fig, ax = plt.subplots()
    ax.hist(df["Amount"], bins=30, color="#4A90D9", edgecolor="white")
    ax.set_title("Distribution of Transaction Amounts")
    ax.set_xlabel("Amount")
    ax.set_ylabel("Frequency")
    path = output_dir / "07_amount_histogram.png"
    _save(fig, path)
    return path


def plot_expense_boxplot(df: pd.DataFrame, output_dir: Path) -> Path:
    """8. Boxplot of expense amounts."""
    fig, ax = plt.subplots()
    expenses = df.loc[df["Type"] == "Expense", "Amount"]
    ax.boxplot(expenses, vert=True, patch_artist=True,
               boxprops=dict(facecolor="#F5B7B1"))
    ax.set_title("Expense Amount Distribution (Boxplot)")
    ax.set_ylabel("Amount")
    path = output_dir / "08_expense_boxplot.png"
    _save(fig, path)
    return path


def plot_income_vs_expense_scatter(df: pd.DataFrame, output_dir: Path) -> Path:
    """9. Scatter plot comparing daily income and expense totals."""
    daily = df.groupby([df["Date"].dt.date, "Type"])["Amount"].sum().unstack(fill_value=0)
    for col in ("Income", "Expense"):
        if col not in daily.columns:
            daily[col] = 0

    fig, ax = plt.subplots()
    ax.scatter(daily["Income"], daily["Expense"], alpha=0.6, color="#8E44AD")
    ax.set_title("Daily Income vs Daily Expense")
    ax.set_xlabel("Income")
    ax.set_ylabel("Expense")
    path = output_dir / "09_income_vs_expense_scatter.png"
    _save(fig, path)
    return path


def plot_category_month_heatmap(df: pd.DataFrame, output_dir: Path) -> Path:
    """10. Heatmap of expense amounts by category and month."""
    from analyzer import MONTH_ORDER

    expenses = df[df["Type"] == "Expense"]
    pivot = expenses.pivot_table(
        index="Category", columns="Month", values="Amount", aggfunc="sum", fill_value=0
    )
    ordered_columns = [m for m in MONTH_ORDER if m in pivot.columns]
    pivot = pivot[ordered_columns]

    fig, ax = plt.subplots(figsize=(12, 7))
    im = ax.imshow(pivot.values, cmap="YlOrRd", aspect="auto")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    ax.set_title("Expenses Heatmap (Category vs Month)")
    fig.colorbar(im, ax=ax, label="Amount")
    path = output_dir / "10_category_month_heatmap.png"
    _save(fig, path)
    return path


def generate_all_charts(df: pd.DataFrame, analysis: AnalysisResult, output_dir: Path) -> list[Path]:
    """Generate every chart required by the project spec and return their paths."""
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Generating charts into %s", output_dir)

    paths = [
        plot_income_line(analysis.monthly.monthly_income, output_dir),
        plot_expense_line(analysis.monthly.monthly_expense, output_dir),
        plot_expense_category_pie(analysis.categories.expense_category_percent, output_dir),
        plot_income_category_pie(analysis.categories.income_category_percent, output_dir),
        plot_expense_category_bar(analysis.categories.top_expense_categories, output_dir),
        plot_income_category_bar(analysis.categories.top_income_categories, output_dir),
        plot_amount_histogram(df, output_dir),
        plot_expense_boxplot(df, output_dir),
        plot_income_vs_expense_scatter(df, output_dir),
        plot_category_month_heatmap(df, output_dir),
    ]
    logger.info("Generated %d charts", len(paths))
    return paths
