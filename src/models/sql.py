import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parents[2] / "local.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
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


def list_services() -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, name, duration_minutes, price_gbp FROM services ORDER BY name ASC"
        ).fetchall()
        return [dict(r) for r in rows]


def get_service(service_id: int) -> dict[str, Any] | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, name, duration_minutes, price_gbp FROM services WHERE id = ?",
            (service_id,),
        ).fetchone()
        return dict(row) if row else None


def create_service(name: str, duration_minutes: int, price_gbp: float) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO services (name, duration_minutes, price_gbp) VALUES (?, ?, ?)",
            (name, duration_minutes, price_gbp),
        )
        conn.commit()
        return int(cur.lastrowid)


def update_service(service_id: int, name: str, duration_minutes: int, price_gbp: float) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE services
            SET name = ?, duration_minutes = ?, price_gbp = ?
            WHERE id = ?
            """,
            (name, duration_minutes, price_gbp, service_id),
        )
        conn.commit()


def delete_service(service_id: int) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM services WHERE id = ?", (service_id,))
        conn.commit()
