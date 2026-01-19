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
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                duration_minutes INTEGER NOT NULL,
                price_gbp REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT NOT NULL,
                scheduled_at TEXT NOT NULL,
                service_id INTEGER NOT NULL,
                created_by_user_id INTEGER NOT NULL,
                FOREIGN KEY (service_id) REFERENCES services(id),
                FOREIGN KEY (created_by_user_id) REFERENCES users(id)
            );
            """
        )
        conn.commit()


# ---------- USERS (AUTH) ----------

def ensure_admin_user(email: str, password_hash: str) -> None:
    email = email.strip().lower()
    with get_conn() as conn:
        row = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if row:
            return
        conn.execute(
            "INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)",
            (email, password_hash, "admin"),
        )
        conn.commit()


def get_user_by_email(email: str) -> dict[str, Any] | None:
    email = email.strip().lower()
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, email, password_hash, role FROM users WHERE email = ?",
            (email,),
        ).fetchone()
        return dict(row) if row else None


# ---------- SERVICES ----------

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


# ---------- APPOINTMENTS ----------

def create_appointment(
    patient_name: str,
    scheduled_at: str,
    service_id: int,
    user_id: int,
) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO appointments
            (patient_name, scheduled_at, service_id, created_by_user_id)
            VALUES (?, ?, ?, ?)
            """,
            (patient_name, scheduled_at, service_id, user_id),
        )
        conn.commit()
        return int(cur.lastrowid)


def list_appointments_for_user(user_id: int, is_admin: bool) -> list[dict[str, Any]]:
    with get_conn() as conn:
        if is_admin:
            rows = conn.execute(
                """
                SELECT a.id, a.patient_name, a.scheduled_at, s.name AS service_name
                FROM appointments a
                JOIN services s ON a.service_id = s.id
                ORDER BY a.id DESC
                """
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT a.id, a.patient_name, a.scheduled_at, s.name AS service_name
                FROM appointments a
                JOIN services s ON a.service_id = s.id
                WHERE a.created_by_user_id = ?
                ORDER BY a.id DESC
                """,
                (user_id,),
            ).fetchall()

        return [dict(r) for r in rows]
