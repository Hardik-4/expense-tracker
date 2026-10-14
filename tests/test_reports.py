from datetime import date

from expense_tracker.database import Expense
from expense_tracker.reports import category_summary, monthly_summary, save_charts, to_dataframe


def sample():
    return to_dataframe([
        Expense(date(2026, 9, 1), 600, "Rent", id=1),
        Expense(date(2026, 9, 3), 40, "Food", id=2),
        Expense(date(2026, 10, 1), 600, "Rent", id=3),
        Expense(date(2026, 10, 4), 60, "Food", id=4),
        Expense(date(2026, 10, 9), 100, "Bills", id=5),
    ])


def test_monthly_summary():
    m = monthly_summary(sample())
    assert list(m["month"]) == ["2026-09", "2026-10"]
    assert list(m["total"]) == [640, 760]
    assert list(m["count"]) == [2, 3]
    assert m["average"].iloc[0] == 320


def test_category_summary_biggest_first():
    c = category_summary(sample())
    assert list(c["category"]) == ["Rent", "Bills", "Food"]
    assert c["total"].iloc[0] == 1200
    assert round(c["percent"].sum()) == 100


def test_category_summary_for_one_month():
    c = category_summary(sample(), "2026-09")
    assert dict(zip(c["category"], c["total"])) == {"Rent": 600, "Food": 40}


def test_empty_data():
    empty = to_dataframe([])
    assert monthly_summary(empty).empty
    assert category_summary(empty).empty
    assert save_charts(empty) == []


def test_charts_are_saved_as_png(tmp_path):
    paths = save_charts(sample(), tmp_path / "charts")
    assert [p.name for p in paths] == ["monthly_spending.png", "category_breakdown.png"]
    for p in paths:
        assert p.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
