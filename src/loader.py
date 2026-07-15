"""
loader.py

Responsible for locating and loading the source Excel file containing
financial transactions into a pandas DataFrame.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

EXPECTED_COLUMNS = [
    "Date",
    "Type",
    "Category",
    "Description",
    "Amount",
    "Payment Method",
    "Month",
]


class DataLoadError(Exception):
    """Raised when the transactions file cannot be found or read."""


def load_transactions(file_path: Path) -> pd.DataFrame:
    """
    Load transactions from an Excel file into a DataFrame.

    Args:
        file_path: Path to the .xlsx file containing transactions.

    Returns:
        A DataFrame with the raw (unclean) transaction data.

    Raises:
        DataLoadError: If the file does not exist or cannot be parsed,
            or if required columns are missing.
    """
    if not file_path.exists():
        message = f"Transactions file not found: {file_path}"
        logger.error(message)
        raise DataLoadError(message)

    try:
        df = pd.read_excel(file_path, sheet_name="Transactions")
    except Exception as exc:  # noqa: BLE001 - surface a clear, user-facing error
        message = f"Failed to read Excel file '{file_path}': {exc}"
        logger.error(message)
        raise DataLoadError(message) from exc

    missing_columns = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    if missing_columns:
        message = f"Missing required columns in '{file_path}': {missing_columns}"
        logger.error(message)
        raise DataLoadError(message)

    logger.info("Loaded %d rows from %s", len(df), file_path)
    return df
