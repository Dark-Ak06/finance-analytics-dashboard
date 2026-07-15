"""
dashboard.py

Interactive console dashboard tying together loading, cleaning,
analysis, chart generation and Excel report creation.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from analyzer import AnalysisResult, run_full_analysis
from charts import generate_all_charts
from cleaner import clean_transactions
from excel_report import build_excel_report
from loader import DataLoadError, load_transactions
from web_export import export_dashboard_json

logger = logging.getLogger(__name__)

MENU_TEXT = """
====================================
   Finance Analytics Dashboard
====================================
1. Load data
2. Clean data
3. Run analysis
4. Generate charts
5. Build Excel report
6. Show key KPIs
7. Exit
------------------------------------
"""


class Dashboard:
    """Stateful console dashboard that orchestrates the analytics pipeline."""

    def __init__(self, data_path: Path, charts_dir: Path, report_path: Path,
                 web_json_path: Path | None = None) -> None:
        self.data_path = data_path
        self.charts_dir = charts_dir
        self.report_path = report_path
        self.web_json_path = web_json_path

        self.raw_df: pd.DataFrame | None = None
        self.clean_df: pd.DataFrame | None = None
        self.analysis: AnalysisResult | None = None
        self.chart_paths: list[Path] = []

    # -- Individual pipeline steps -----------------------------------------

    def load_data(self) -> None:
        try:
            self.raw_df = load_transactions(self.data_path)
            print(f"Loaded {len(self.raw_df)} rows from {self.data_path}")
        except DataLoadError as exc:
            print(f"Error loading data: {exc}")

    def clean_data(self) -> None:
        if self.raw_df is None:
            print("Please load data first (option 1).")
            return
        self.clean_df = clean_transactions(self.raw_df)
        print(f"Cleaning complete. {len(self.clean_df)} valid row(s) remain.")

    def run_analysis(self) -> None:
        if self.clean_df is None:
            print("Please clean data first (option 2).")
            return
        self.analysis = run_full_analysis(self.clean_df)
        print("Analysis complete.")

    def build_charts(self) -> None:
        if self.clean_df is None or self.analysis is None:
            print("Please run analysis first (option 3).")
            return
        self.chart_paths = generate_all_charts(self.clean_df, self.analysis, self.charts_dir)
        print(f"Generated {len(self.chart_paths)} chart(s) in {self.charts_dir}")

    def build_report(self) -> None:
        if self.clean_df is None or self.analysis is None:
            print("Please run analysis first (option 3).")
            return
        if not self.chart_paths:
            print("No charts found yet — generating them first.")
            self.build_charts()
        path = build_excel_report(self.clean_df, self.analysis, self.chart_paths, self.report_path)
        print(f"Excel report saved to {path}")

        if self.web_json_path is not None:
            export_dashboard_json(self.clean_df, self.analysis, self.web_json_path)
            print(f"Web dashboard data updated at {self.web_json_path}")

    def show_kpis(self) -> None:
        if self.analysis is None:
            print("Please run analysis first (option 3).")
            return
        overall = self.analysis.overall
        print("\n--- Key Performance Indicators ---")
        print(f"Total Income:        {overall.total_income:,.2f}")
        print(f"Total Expense:       {overall.total_expense:,.2f}")
        print(f"Net Profit:          {overall.net_profit:,.2f}")
        print(f"Average Expense:     {overall.average_expense:,.2f}")
        print(f"Average Income:      {overall.average_income:,.2f}")
        print(f"Total Transactions:  {overall.total_transactions}")
        print(f"Most Expensive Cat.: {self.analysis.categories.most_expensive_category}")
        print(f"Most Profitable Cat: {self.analysis.categories.most_profitable_category}")
        print(f"Most Used Payment:   {self.analysis.payments.most_used_method}")
        print("-----------------------------------\n")

    def run_full_pipeline(self) -> None:
        """Run every step in order, useful for non-interactive execution."""
        self.load_data()
        self.clean_data()
        self.run_analysis()
        self.build_charts()
        self.build_report()
        self.show_kpis()

    # -- Interactive loop -----------------------------------------------

    def run_menu(self) -> None:
        actions = {
            "1": self.load_data,
            "2": self.clean_data,
            "3": self.run_analysis,
            "4": self.build_charts,
            "5": self.build_report,
            "6": self.show_kpis,
        }

        while True:
            print(MENU_TEXT)
            choice = input("Select an option (1-7): ").strip()

            if choice == "7":
                print("Goodbye!")
                break

            action = actions.get(choice)
            if action is None:
                print("Invalid option, please choose a number between 1 and 7.")
                continue

            try:
                action()
            except Exception as exc:  # noqa: BLE001 - keep the dashboard alive on error
                logger.exception("Unexpected error while running dashboard action")
                print(f"An unexpected error occurred: {exc}")
