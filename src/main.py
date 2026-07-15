"""
main.py

Entry point for the Finance Analytics Dashboard.

Run with:
    python src/main.py            # interactive console menu
    python src/main.py --auto     # run the full pipeline once, no menu
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from dashboard import Dashboard  # noqa: E402

DATA_PATH = PROJECT_ROOT / "data" / "transactions.xlsx"
CHARTS_DIR = PROJECT_ROOT / "charts"
REPORT_PATH = PROJECT_ROOT / "reports" / "Finance_Report.xlsx"
WEB_JSON_PATH = PROJECT_ROOT / "docs" / "data" / "dashboard_data.json"
LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "app.log"


def configure_logging() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def ensure_sample_data_exists() -> None:
    """Create sample transaction data on first run if none exists yet."""
    if DATA_PATH.exists():
        return
    from generate_sample_data import save_sample_data

    logging.getLogger(__name__).info("No transactions file found, generating sample data")
    save_sample_data(DATA_PATH)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Finance Analytics Dashboard")
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Run the full pipeline once (load, clean, analyze, charts, report) without the menu.",
    )
    return parser.parse_args()


def main() -> None:
    configure_logging()
    ensure_sample_data_exists()

    args = parse_args()
    dashboard = Dashboard(
        data_path=DATA_PATH,
        charts_dir=CHARTS_DIR,
        report_path=REPORT_PATH,
        web_json_path=WEB_JSON_PATH,
    )

    try:
        if args.auto:
            dashboard.run_full_pipeline()
        else:
            dashboard.run_menu()
    except KeyboardInterrupt:
        print("\nInterrupted. Goodbye!")


if __name__ == "__main__":
    main()
