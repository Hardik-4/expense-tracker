import pytest

from expense_tracker.database import ExpenseDB


@pytest.fixture
def db(tmp_path):
    """A brand-new database file for each test."""
    database = ExpenseDB(str(tmp_path / "test.db"))
    yield database
    database.close()
