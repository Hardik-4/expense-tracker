"""Importing and exporting expenses as CSV files (columns: date,amount,category,description)."""
from pathlib import Path

import pandas as pd

from .database import Expense, ExpenseDB, validate
from .reports import to_dataframe

CSV_COLUMNS = ["date", "amount", "category", "description"]


def export_csv(db: ExpenseDB, path: str | Path) -> int:
    """Writes every expense to a CSV file. Returns the number of rows written."""
    df = to_dataframe(db.all())
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    df[CSV_COLUMNS].to_csv(path, index=False)
    return len(df)


def import_csv(db: ExpenseDB, path: str | Path) -> tuple[int, list[str]]:
    """Reads a CSV file and adds the valid rows.
    Returns (number imported, list of error messages for skipped rows). Bad rows don't stop the import."""
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    missing = set(CSV_COLUMNS[:3]) - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing column(s): {', '.join(sorted(missing))}")

    imported, errors = 0, []
    for i, row in df.iterrows():
        line = i + 2  # +1 for the header, +1 because people count from 1
        try:
            expense = Expense(
                date=pd.to_datetime(row["date"], format="%Y-%m-%d").date(),
                amount=row["amount"],
                category=row["category"],
                description=row.get("description", ""),
            )
            db.add(validate(expense))
            imported += 1
        except (ValueError, TypeError) as err:
            errors.append(f"line {line}: {err}")
    return imported, errors
