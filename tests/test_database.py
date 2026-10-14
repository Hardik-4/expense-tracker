from datetime import date

import pytest

from expense_tracker.database import Expense


def test_add_and_get(db):
    e = db.add(Expense(date(2026, 10, 1), "12.345", " food ", " lunch "))
    assert e.id is not None
    saved = db.get(e.id)
    assert saved == Expense(date(2026, 10, 1), 12.35, "Food", "lunch", e.id)  # cleaned up


def test_update(db):
    e = db.add(Expense(date(2026, 10, 1), 10, "Food"))
    db.update(Expense(date(2026, 10, 2), 20, "Transport", "bus", e.id))
    assert db.get(e.id).amount == 20
    assert db.get(e.id).category == "Transport"


def test_delete(db):
    e = db.add(Expense(date(2026, 10, 1), 10, "Food"))
    db.delete(e.id)
    assert db.get(e.id) is None
    with pytest.raises(KeyError):
        db.delete(e.id)


def test_update_missing_raises(db):
    with pytest.raises(KeyError):
        db.update(Expense(date(2026, 10, 1), 10, "Food", "", 999))


@pytest.mark.parametrize("amount,category", [(0, "Food"), (-5, "Food"), ("abc", "Food"), (10, "Pizza"), (10, "")])
def test_invalid_expenses_are_rejected(db, amount, category):
    with pytest.raises(ValueError):
        db.add(Expense(date(2026, 10, 1), amount, category))


def test_all_is_sorted_by_date(db):
    db.add(Expense(date(2026, 10, 5), 1, "Food"))
    db.add(Expense(date(2026, 10, 1), 1, "Food"))
    assert [e.date.day for e in db.all()] == [1, 5]


def test_quotes_are_stored_safely(db):
    text = "Robert'); DROP TABLE expense;--"
    e = db.add(Expense(date(2026, 10, 1), 1, "Other", text))
    assert db.get(e.id).description == text
    assert len(db.all()) == 1
