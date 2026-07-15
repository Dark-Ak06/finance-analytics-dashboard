"""
cleaner.py

Cleans raw transaction data: removes empty rows, duplicates, validates
dates, checks for negative amounts, fills missing values, and logs
every issue found along the way.
"""

from __future__ import annotations

import logging

import pandas as pd

logger = logging.getLogger(__name__)

REQUIRED_NON_NULL_COLUMNS = ["Date", "Type", "Category", "Amount"]


def _drop_empty_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows that are completely empty or missing all key fields."""
    before = len(df)
    df = df.dropna(how="all")
    df = df.dropna(subset=REQUIRED_NON_NULL_COLUMNS, how="all")
    removed = before - len(df)
    if removed:
        logger.warning("Removed %d completely empty row(s)", removed)
    return df


def _drop_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove exact duplicate transaction rows."""
    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)
    if removed:
        logger.warning("Removed %d duplicate row(s)", removed)
    return df


def _validate_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Convert the Date column to datetime, logging unparsable dates."""
    original = df["Date"]
    converted = pd.to_datetime(original, errors="coerce")
    invalid_mask = converted.isna() & original.notna()
    if invalid_mask.any():
        logger.warning("Found %d row(s) with invalid dates", int(invalid_mask.sum()))
    df = df.copy()
    df["Date"] = converted
    return df


def _fix_negative_amounts(df: pd.DataFrame) -> pd.DataFrame:
    """Convert negative amounts to their absolute value and log a warning."""
    df = df.copy()
    negative_mask = df["Amount"] < 0
    count = int(negative_mask.sum())
    if count:
        logger.warning("Found %d row(s) with negative amounts; converted to absolute value", count)
        df.loc[negative_mask, "Amount"] = df.loc[negative_mask, "Amount"].abs()
    return df


def _fill_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing categorical values with 'Unknown' and recompute Month."""
    df = df.copy()

    for column in ["Type", "Category", "Description", "Payment Method"]:
        missing_count = int(df[column].isna().sum())
        if missing_count:
            logger.warning("Filled %d missing value(s) in column '%s'", missing_count, column)
            df[column] = df[column].fillna("Unknown")

    missing_amount = int(df["Amount"].isna().sum())
    if missing_amount:
        logger.warning("Filled %d missing value(s) in column 'Amount' with 0", missing_amount)
        df["Amount"] = df["Amount"].fillna(0)

    # Recompute Month from Date so it is always consistent, even where the
    # original file had a missing or incorrect Month value.
    df["Month"] = df["Date"].dt.month_name()
    df["Month"] = df["Month"].fillna("Unknown")

    return df


def _drop_rows_without_valid_date(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows where the date could not be determined at all."""
    before = len(df)
    df = df.dropna(subset=["Date"])
    removed = before - len(df)
    if removed:
        logger.warning("Removed %d row(s) with unrecoverable/missing dates", removed)
    return df


def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run the full cleaning pipeline on the raw transactions DataFrame.

    Steps:
        1. Drop completely empty rows.
        2. Drop duplicate rows.
        3. Validate and normalize dates.
        4. Fix negative amounts.
        5. Fill missing values.
        6. Drop rows whose date could not be recovered.

    Args:
        df: Raw DataFrame as loaded from Excel.

    Returns:
        A cleaned copy of the DataFrame, ready for analysis.
    """
    logger.info("Starting data cleaning on %d row(s)", len(df))

    df = _drop_empty_rows(df)
    df = _drop_duplicates(df)
    df = _validate_dates(df)
    df = _fix_negative_amounts(df)
    df = _fill_missing_values(df)
    df = _drop_rows_without_valid_date(df)

    df = df.reset_index(drop=True)
    logger.info("Cleaning complete. %d row(s) remain", len(df))
    return df
