import sqlite3
from datetime import datetime

DB_NAME = "rates.db"


def init_db() -> None:

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS rates (
                id INTEGER PRIMARY KEY,
                currency TEXT NOT NULL,
                rate REAL NOT NULL,
                fetched_at TEXT NOT NULL
            )
        """)
        conn.commit()


def save_rate(id: int, target_currency: str, rate: float) -> None:

    date_str = datetime.now().isoformat()
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO rates (id, currency, rate, fetched_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                rate = excluded.rate,
                fetched_at = excluded.fetched_at
        """,
            (id, target_currency, rate, date_str),
        )
        conn.commit()


def get_saved_rate(target_currency: str) -> float:

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT rate FROM rates WHERE currency = ?", (target_currency,))
        row = cur.fetchone()
        return row[0] if row else None
