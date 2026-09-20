import os
import sqlite3

import pytest

from db import init_db, save_rate, get_saved_rate


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    """Каждый тест получает свою временную БД."""
    db_file = tmp_path / "test.db"
    monkeypatch.setattr("db.DB_NAME", str(db_file))
    init_db()
    yield
    try:
        if os.path.exists(db_file):
            os.remove(db_file)
    except PermissionError:
        pass


def test_init_db_creates_table():
    from db import DB_NAME
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cur.fetchall()]
    assert "rates" in tables


def test_save_rate_new_record():
    save_rate(1, "USD", 90.5)
    assert get_saved_rate("USD") == 90.5


def test_save_rate_update_existing():
    save_rate(1, "USD", 90.5)
    save_rate(1, "USD", 95.0)
    assert get_saved_rate("USD") == 95.0


def test_save_rate_date_format():
    from db import DB_NAME
    save_rate(1, "USD", 90.5)
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT fetched_at FROM rates WHERE currency = 'USD'")
        fetched = cur.fetchone()[0]
    assert "T" in fetched


def test_save_rate_multiple_currencies():
    save_rate(1, "USD", 90.5)
    save_rate(2, "EUR", 100.2)
    assert get_saved_rate("USD") == 90.5
    assert get_saved_rate("EUR") == 100.2


def test_save_rate_edge_cases():
    save_rate(1, "USD", 0.001)
    assert get_saved_rate("USD") == 0.001
    save_rate(2, "EUR", 99999.99)
    assert get_saved_rate("EUR") == 99999.99


def test_save_rate_database_connection_error(monkeypatch):
    def broken_connect(*args, **kwargs):
        raise sqlite3.OperationalError("connection failed")
    monkeypatch.setattr(sqlite3, "connect", broken_connect)
    with pytest.raises(sqlite3.OperationalError):
        save_rate(1, "USD", 90.5)


def test_save_rate_commit_error(monkeypatch):
    class FakeConn:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def cursor(self):
            class Cur:
                def execute(self, *args, **kwargs): pass
            return Cur()
        def commit(self):
            raise sqlite3.OperationalError("commit failed")
    monkeypatch.setattr(sqlite3, "connect", lambda *a, **kw: FakeConn())
    with pytest.raises(sqlite3.OperationalError):
        save_rate(1, "USD", 90.5)


def test_save_rate_parameter_types():
    save_rate(1, "USD", 90)
    assert get_saved_rate("USD") == 90
    save_rate(2, "EUR", 90.5)
    assert get_saved_rate("EUR") == 90.5


def test_save_rate_sql_injection_protection():
    save_rate(1, "USD'; DROP TABLE rates; --", 90.5)
    assert get_saved_rate("USD'; DROP TABLE rates; --") == 90.5


def test_get_saved_rate_success():
    save_rate(1, "USD", 90.5)
    assert get_saved_rate("USD") == 90.5


def test_get_saved_rate_default_currency():
    save_rate(1, "RUB", 1.0)
    assert get_saved_rate("RUB") == 1.0


def test_get_saved_rate_nonexistent_currency():
    assert get_saved_rate("XYZ") is None


def test_get_saved_rate_empty_database():
    assert get_saved_rate("USD") is None


def test_get_saved_rate_multiple_currencies():
    save_rate(1, "USD", 90.5)
    save_rate(2, "EUR", 100.2)
    save_rate(3, "CNY", 12.7)
    assert get_saved_rate("USD") == 90.5
    assert get_saved_rate("EUR") == 100.2
    assert get_saved_rate("CNY") == 12.7


def test_get_saved_rate_case_sensitivity():
    save_rate(1, "USD", 90.5)
    assert get_saved_rate("usd") is None


def test_get_saved_rate_sql_injection_protection():
    assert get_saved_rate("'; DROP TABLE rates; --") is None


def test_get_saved_rate_database_connection_error(monkeypatch):
    def broken_connect(*args, **kwargs):
        raise sqlite3.OperationalError("connection failed")
    monkeypatch.setattr(sqlite3, "connect", broken_connect)
    with pytest.raises(sqlite3.OperationalError):
        get_saved_rate("USD")