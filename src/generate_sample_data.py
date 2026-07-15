"""
generate_sample_data.py

Generates a realistic sample Excel file with financial transactions
(data/transactions.xlsx). Used to seed the project with data so the
dashboard, charts and report can be produced without any manual setup.

Run directly:
    python src/generate_sample_data.py
"""

from __future__ import annotations

import random
from datetime import date
from pathlib import Path

import pandas as pd

RANDOM_SEED = 42
NUMBER_OF_RECORDS = 650

EXPENSE_CATEGORIES = [
    "Food",
    "Transport",
    "Entertainment",
    "Shopping",
    "Rent",
    "Utilities",
    "Health",
    "Education",
    "Travel",
    "Subscriptions",
    "Internet",
    "Mobile",
    "Gift",
    "Other",
]

INCOME_CATEGORIES = ["Salary", "Bonus", "Freelance", "Investment", "Gift", "Other"]

PAYMENT_METHODS = ["Card", "Cash", "Bank"]

MONTH_NAMES = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

EXPENSE_DESCRIPTIONS = {
    "Food": ["McDonald's", "Grocery store", "Coffee shop", "Restaurant dinner", "Supermarket"],
    "Transport": ["Taxi ride", "Metro card top-up", "Fuel", "Parking", "Bus ticket"],
    "Entertainment": ["Cinema tickets", "Concert", "Streaming rental", "Bowling", "Video game"],
    "Shopping": ["Clothing store", "Electronics", "Online marketplace", "Shoes", "Accessories"],
    "Rent": ["Monthly apartment rent"],
    "Utilities": ["Electricity bill", "Water bill", "Gas bill", "Heating bill"],
    "Health": ["Pharmacy", "Doctor visit", "Dental checkup", "Vitamins", "Gym membership"],
    "Education": ["Online course", "Textbooks", "Tuition fee", "Workshop fee"],
    "Travel": ["Flight ticket", "Hotel booking", "Train ticket", "Travel insurance"],
    "Subscriptions": ["Streaming service", "Cloud storage", "Magazine", "Software license"],
    "Internet": ["Home internet bill"],
    "Mobile": ["Mobile plan top-up"],
    "Gift": ["Birthday gift", "Wedding gift", "Holiday gift"],
    "Other": ["Miscellaneous purchase", "Bank fee", "Service fee"],
}

INCOME_DESCRIPTIONS = {
    "Salary": ["Monthly salary"],
    "Bonus": ["Performance bonus", "Year-end bonus"],
    "Freelance": ["Freelance project payment", "Consulting fee"],
    "Investment": ["Dividend payout", "Stock sale profit", "Interest income"],
    "Gift": ["Gift received"],
    "Other": ["Cashback", "Refund", "Miscellaneous income"],
}

# Typical amount ranges (in local currency units) per category, used to
# generate plausible random amounts.
EXPENSE_AMOUNT_RANGES = {
    "Food": (1500, 15000),
    "Transport": (500, 8000),
    "Entertainment": (2000, 20000),
    "Shopping": (3000, 60000),
    "Rent": (120000, 220000),
    "Utilities": (8000, 30000),
    "Health": (2000, 40000),
    "Education": (10000, 150000),
    "Travel": (20000, 250000),
    "Subscriptions": (1500, 9000),
    "Internet": (5000, 12000),
    "Mobile": (2000, 8000),
    "Gift": (3000, 30000),
    "Other": (500, 10000),
}

INCOME_AMOUNT_RANGES = {
    "Salary": (350000, 500000),
    "Bonus": (50000, 200000),
    "Freelance": (30000, 250000),
    "Investment": (5000, 80000),
    "Gift": (5000, 50000),
    "Other": (1000, 20000),
}


def _month_name_for(d: date) -> str:
    """Return the English month name for a given date."""
    return MONTH_NAMES[d.month - 1]


def _random_date(start: date, end: date, rng: random.Random) -> date:
    """Return a random date between start and end (inclusive)."""
    delta_days = (end - start).days
    offset = rng.randint(0, delta_days)
    return date.fromordinal(start.toordinal() + offset)


def _build_expense_row(rng: random.Random, d: date) -> dict:
    category = rng.choice(EXPENSE_CATEGORIES)
    low, high = EXPENSE_AMOUNT_RANGES[category]
    amount = round(rng.uniform(low, high), -2)  # round to nearest 100
    description = rng.choice(EXPENSE_DESCRIPTIONS[category])
    return {
        "Date": d,
        "Type": "Expense",
        "Category": category,
        "Description": description,
        "Amount": amount,
        "Payment Method": rng.choice(PAYMENT_METHODS),
        "Month": _month_name_for(d),
    }


def _build_income_row(rng: random.Random, d: date) -> dict:
    category = rng.choice(INCOME_CATEGORIES)
    low, high = INCOME_AMOUNT_RANGES[category]
    amount = round(rng.uniform(low, high), -2)
    description = rng.choice(INCOME_DESCRIPTIONS[category])
    return {
        "Date": d,
        "Type": "Income",
        "Category": category,
        "Description": description,
        "Amount": amount,
        "Payment Method": rng.choice(["Bank", "Card"]),
        "Month": _month_name_for(d),
    }


def generate_transactions(number_of_records: int = NUMBER_OF_RECORDS,
                           seed: int = RANDOM_SEED) -> pd.DataFrame:
    """Generate a DataFrame of random but realistic financial transactions."""
    rng = random.Random(seed)
    start_date = date(2026, 1, 1)
    end_date = date(2026, 12, 31)

    rows: list[dict] = []

    # Guarantee 12 monthly salary payments (one per month, around the 5th).
    for month_index in range(1, 13):
        salary_day = date(2026, month_index, 5)
        rows.append(_build_income_row(rng, salary_day) | {
            "Category": "Salary",
            "Description": "Monthly salary",
            "Amount": round(rng.uniform(*INCOME_AMOUNT_RANGES["Salary"]), -2),
            "Payment Method": "Bank",
        })
        # Guarantee monthly rent expense too.
        rows.append(_build_expense_row(rng, date(2026, month_index, 2)) | {
            "Category": "Rent",
            "Description": "Monthly apartment rent",
            "Amount": round(rng.uniform(*EXPENSE_AMOUNT_RANGES["Rent"]), -2),
        })

    remaining = number_of_records - len(rows)
    expense_share = 0.75

    for _ in range(remaining):
        d = _random_date(start_date, end_date, rng)
        if rng.random() < expense_share:
            rows.append(_build_expense_row(rng, d))
        else:
            rows.append(_build_income_row(rng, d))

    # Inject a handful of intentionally messy rows so cleaner.py has
    # something real to clean (duplicates, blanks, negative amount).
    if len(rows) >= 5:
        duplicate_row = dict(rows[10])
        rows.append(duplicate_row)  # duplicate

        messy_row = dict(rows[20])
        messy_row["Amount"] = -abs(messy_row["Amount"])  # negative amount
        rows.append(messy_row)

        blank_row = {
            "Date": None,
            "Type": None,
            "Category": None,
            "Description": None,
            "Amount": None,
            "Payment Method": None,
            "Month": None,
        }
        rows.append(blank_row)

    df = pd.DataFrame(rows)
    df = df.sort_values(by="Date", na_position="last").reset_index(drop=True)
    return df


def save_sample_data(output_path: Path) -> Path:
    """Generate sample transactions and save them as an Excel file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df = generate_transactions()
    df.to_excel(output_path, index=False, sheet_name="Transactions")
    return output_path


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    target = project_root / "data" / "transactions.xlsx"
    saved_path = save_sample_data(target)
    print(f"Sample data generated: {saved_path} ({NUMBER_OF_RECORDS} rows)")
