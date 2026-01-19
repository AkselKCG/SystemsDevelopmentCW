import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "local.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                duration_minutes INTEGER NOT NULL,
                price_gbp REAL NOT NULL
            )
            """
        )
        conn.commit()

def list_services():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, name, duration_minutes, price_gbp FROM services ORDER BY name ASC"
        ).fetchall()
        return [dict(r) for r in rows]

def create_service(name: str, duration_minutes: int, price_gbp: float):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO services (name, duration_minutes, price_gbp) VALUES (?, ?, ?)",
            (name, duration_minutes, price_gbp),
        )
        conn.commit()
