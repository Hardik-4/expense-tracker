from expense_tracker.cli import run


def feed(monkeypatch, answers):
    it = iter(answers)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(it))


def test_add_list_delete_through_menu(db, monkeypatch, capsys):
    feed(monkeypatch, ["1", "2026-10-01", "12.5", "food", "lunch",   # add
                       "4",                                          # list
                       "3", "1",                                     # delete id 1
                       "0"])
    run(db)
    out = capsys.readouterr().out
    assert "Added expense #1" in out
    assert "lunch" in out and "Total: 12.50" in out
    assert db.all() == []


def test_bad_input_does_not_crash(db, monkeypatch, capsys):
    feed(monkeypatch, ["1", "2026-10-01", "-3", "Food", "", "x", "0"])
    run(db)
    out = capsys.readouterr().out
    assert "Error: amount must be greater than 0" in out
    assert "Please choose 0-9" in out
