"""The command-line menu. Run with:  python -m expense_tracker"""
from datetime import date

from .csv_io import export_csv, import_csv
from .database import CATEGORIES, Expense, ExpenseDB
from .reports import category_summary, monthly_summary, save_charts, to_dataframe

MENU = """
===== Expense Tracker =====
1. Add expense
2. Edit expense
3. Delete expense
4. List expenses
5. Monthly summary
6. Category summary
7. Save charts (PNG)
8. Import CSV
9. Export CSV
0. Quit
"""


def ask(prompt: str, default: str | None = None) -> str:
    """input() that returns the default when the user just presses Enter."""
    suffix = f" [{default}]" if default is not None else ""
    answer = input(f"{prompt}{suffix}: ").strip()
    return answer if answer else (default or "")


def ask_expense(old: Expense | None = None) -> Expense:
    """Asks for each field. When editing, the current value is shown and kept if Enter is pressed."""
    print("Categories:", ", ".join(CATEGORIES))
    d = ask("Date (YYYY-MM-DD)", old.date.isoformat() if old else date.today().isoformat())
    amount = ask("Amount", str(old.amount) if old else None)
    category = ask("Category", old.category if old else None)
    description = ask("Description", old.description if old else "")
    return Expense(date.fromisoformat(d), amount, category, description, old.id if old else None)


def print_expenses(expenses: list[Expense]) -> None:
    if not expenses:
        print("No expenses yet.")
        return
    print(f"{'ID':>4}  {'Date':10}  {'Amount':>9}  {'Category':13}  Description")
    for e in expenses:
        print(f"{e.id:>4}  {e.date.isoformat():10}  {e.amount:>9.2f}  {e.category:13}  {e.description}")
    print(f"Total: {sum(e.amount for e in expenses):.2f}")


def run(db: ExpenseDB) -> None:
    while True:
        print(MENU)
        choice = input("Choose: ").strip()
        try:
            if choice == "1":
                e = db.add(ask_expense())
                print(f"Added expense #{e.id}.")
            elif choice == "2":
                old = db.get(int(ask("ID to edit")))
                if old is None:
                    print("Not found.")
                else:
                    db.update(ask_expense(old))
                    print("Updated.")
            elif choice == "3":
                db.delete(int(ask("ID to delete")))
                print("Deleted.")
            elif choice == "4":
                print_expenses(db.all())
            elif choice == "5":
                print(monthly_summary(to_dataframe(db.all())).to_string(index=False))
            elif choice == "6":
                month = ask("Month YYYY-MM (Enter for all)", "") or None
                print(category_summary(to_dataframe(db.all()), month).to_string(index=False))
            elif choice == "7":
                paths = save_charts(to_dataframe(db.all()))
                print("Saved:", ", ".join(map(str, paths)) if paths else "nothing (no data)")
            elif choice == "8":
                count, errors = import_csv(db, ask("CSV file to import"))
                print(f"Imported {count} expense(s).")
                for err in errors:
                    print("  skipped", err)
            elif choice == "9":
                path = ask("Export to", "expenses_export.csv")
                print(f"Exported {export_csv(db, path)} expense(s) to {path}.")
            elif choice == "0":
                print("Bye!")
                return
            else:
                print("Please choose 0-9.")
        # show a friendly message instead of crashing on bad input
        except (ValueError, KeyError, FileNotFoundError) as err:
            print("Error:", err)


def main() -> None:
    db = ExpenseDB("expenses.db")
    try:
        run(db)
    finally:
        db.close()
