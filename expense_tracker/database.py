"""All SQLite access lives here. Every query uses ? placeholders, which prevents SQL injection."""
import sqlite3
from dataclasses import dataclass
from datetime import date

CATEGORIES = ["Food", "Transport", "Rent", "Bills", "Entertainment", "Shopping", "Health", "Education", "Other"]


@dataclass
class Expense:
    """One expense. The id is None until the expense is saved."""
    date: date
    amount: float
    category: str
    description: str = ""
    id: int | None = None


def validate(e: Expense) -> Expense:
    """Checks the values and returns a cleaned-up copy. Raises ValueError if something is wrong."""
    if not isinstance(e.date, date):
        raise ValueError("date must be a date")
    try:
        amount = round(float(e.amount), 2)
    except (TypeError, ValueError):
        raise ValueError("amount must be a number")
    if amount <= 0:
        raise ValueError("amount must be greater than 0")
    category = (e.category or "").strip().title()
    if category not in CATEGORIES:
        raise ValueError(f"category must be one of: {', '.join(CATEGORIES)}")
    return Expense(e.date, amount, category, (e.description or "").strip(), e.id)


class ExpenseDB:
    def __init__(self, path: str = "expenses.db"):
        self.conn = sqlite3.connect(path)
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS expense (
                   id          INTEGER PRIMARY KEY AUTOINCREMENT,
                   date        TEXT NOT NULL,          -- stored as YYYY-MM-DD
                   amount      REAL NOT NULL CHECK (amount > 0),
                   category    TEXT NOT NULL,
                   description TEXT NOT NULL DEFAULT ''
               )"""
        )
        self.conn.commit()

    def add(self, e: Expense) -> Expense:
        e = validate(e)
        cur = self.conn.execute(
            "INSERT INTO expense (date, amount, category, description) VALUES (?, ?, ?, ?)",
            (e.date.isoformat(), e.amount, e.category, e.description),
        )
        self.conn.commit()
        e.id = cur.lastrowid
        return e

    def update(self, e: Expense) -> None:
        e = validate(e)
        cur = self.conn.execute(
            "UPDATE expense SET date = ?, amount = ?, category = ?, description = ? WHERE id = ?",
            (e.date.isoformat(), e.amount, e.category, e.description, e.id),
        )
        self.conn.commit()
        if cur.rowcount == 0:
            raise KeyError(f"No expense with id {e.id}")

    def delete(self, expense_id: int) -> None:
        cur = self.conn.execute("DELETE FROM expense WHERE id = ?", (expense_id,))
        self.conn.commit()
        if cur.rowcount == 0:
            raise KeyError(f"No expense with id {expense_id}")

    def get(self, expense_id: int) -> Expense | None:
        row = self.conn.execute(
            "SELECT id, date, amount, category, description FROM expense WHERE id = ?", (expense_id,)
        ).fetchone()
        return self._to_expense(row) if row else None

    def all(self) -> list[Expense]:
        rows = self.conn.execute(
            "SELECT id, date, amount, category, description FROM expense ORDER BY date, id"
        ).fetchall()
        return [self._to_expense(r) for r in rows]

    def close(self) -> None:
        self.conn.close()

    @staticmethod
    def _to_expense(row) -> Expense:
        return Expense(id=row[0], date=date.fromisoformat(row[1]), amount=row[2], category=row[3], description=row[4])
