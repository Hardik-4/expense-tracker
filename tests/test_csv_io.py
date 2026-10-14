from datetime import date
from pathlib import Path

import pytest

from expense_tracker.csv_io import export_csv, import_csv
from expense_tracker.database import Expense

SAMPLE = Path(__file__).parent.parent / "sample_expenses.csv"


def test_import_sample_file(db):
    count, errors = import_csv(db, SAMPLE)
    assert count == 10 and errors == []
    assert sum(e.amount for e in db.all()) == pytest.approx(2267.44)


def test_export_then_import_round_trip(db, tmp_path):
    db.add(Expense(date(2026, 10, 1), 9.99, "Food", "pizza, large"))  # comma inside text
    db.add(Expense(date(2026, 10, 2), 3.5, "Transport"))
    out = tmp_path / "out.csv"
    assert export_csv(db, out) == 2

    from expense_tracker.database import ExpenseDB
    other = ExpenseDB(str(tmp_path / "other.db"))
    assert import_csv(other, out) == (2, [])
    assert [(e.date, e.amount, e.category, e.description) for e in other.all()] == \
           [(e.date, e.amount, e.category, e.description) for e in db.all()]
    other.close()


def test_bad_rows_are_skipped_with_messages(db, tmp_path):
    f = tmp_path / "bad.csv"
    f.write_text("date,amount,category,description\n"
                 "2026-10-01,10,Food,ok\n"
                 "not-a-date,10,Food,x\n"
                 "2026-10-02,-1,Food,x\n"
                 "2026-10-03,5,Spaceships,x\n")
    count, errors = import_csv(db, f)
    assert count == 1
    assert [e.split(":")[0] for e in errors] == ["line 3", "line 4", "line 5"]


def test_missing_columns(db, tmp_path):
    f = tmp_path / "wrong.csv"
    f.write_text("when,how_much\n2026-10-01,5\n")
    with pytest.raises(ValueError, match="missing column"):
        import_csv(db, f)
