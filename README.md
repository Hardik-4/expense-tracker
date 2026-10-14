# Expense Tracker

A command-line app for tracking personal spending. It uses **Python 3, SQLite, pandas and Matplotlib**, and is small and well-commented so a student can explain every part.

## Features
- A menu to **add, edit, delete and list** expenses (date, amount, category, description).
- Input is checked: the amount must be greater than 0, the category must come from a fixed list, and the date must be in YYYY-MM-DD format.
- **Monthly summary** (total, count and average per month) and **category summary** (total and % share, for all months or a single month).
- Charts are saved as **PNG**: `charts/monthly_spending.png` (bar chart) and `charts/category_breakdown.png` (pie chart).
- **CSV import/export**. Bad rows are skipped and the line number is reported. Try it with `sample_expenses.csv`.
- SQL uses `?` placeholders, so it is safe from SQL injection.

## Architecture
| Module | Job |
|---|---|
| `database.py` | `Expense` dataclass, `validate()`, `ExpenseDB` (SQLite CRUD) |
| `reports.py` | pandas DataFrame, monthly and category summaries, Matplotlib charts |
| `csv_io.py` | CSV import/export |
| `cli.py` | Menu and user input; it only calls the modules above |

Data flows like this: `cli -> database (SQLite file expenses.db)`, and `cli -> reports/csv_io -> pandas`.

## Run
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m expense_tracker
```
Choose option 8 and enter `sample_expenses.csv` to load some example data.

## Test
```bash
pytest
```
There are 22 tests covering CRUD, validation, summaries, PNG chart output, the CSV round-trip and bad rows, and the menu (using fake keyboard input). Each test uses its own temporary database.
