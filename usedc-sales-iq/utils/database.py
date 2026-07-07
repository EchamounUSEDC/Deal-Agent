"""
utils/database.py — schema + query helpers.

The `calls` table is the shared contract between modules: Asa's Call
Analyzer writes rows (source='analyzed'), Ayan's tabs read them. SQLite
today; every query goes through the helpers below so a Postgres swap
only touches this file.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DATA_DIR / "sales_iq.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS calls (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    call_time          TEXT NOT NULL,               -- ISO 8601
    rep_name           TEXT NOT NULL,
    territory          TEXT,
    customer_name      TEXT,
    duration_min       REAL,
    product_interest   TEXT,
    objections         TEXT,                        -- JSON array of strings
    outcome            TEXT,                        -- converted | follow_up | no_sale
    score              INTEGER,                     -- 0-100 call quality
    summary            TEXT,
    transcript_snippet TEXT,                        -- a line the rep actually said
    source             TEXT NOT NULL DEFAULT 'analyzed',  -- analyzed | sample
    created_at         TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_calls_rep  ON calls (rep_name);
CREATE INDEX IF NOT EXISTS idx_calls_time ON calls (call_time);

CREATE TABLE IF NOT EXISTS coach_notes (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    rep_name   TEXT NOT NULL,
    note       TEXT NOT NULL,
    author     TEXT NOT NULL DEFAULT 'Manager',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

OUTCOMES = ("converted", "follow_up", "no_sale")


def get_conn() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(_SCHEMA)


def count_calls() -> int:
    with get_conn() as conn:
        return conn.execute("SELECT COUNT(*) FROM calls").fetchone()[0]


def insert_calls(rows: list[dict]) -> None:
    """Bulk-insert call rows. `objections` may be a list; it is stored as JSON."""
    cols = (
        "call_time", "rep_name", "territory", "customer_name", "duration_min",
        "product_interest", "objections", "outcome", "score", "summary",
        "transcript_snippet", "source",
    )
    prepared = []
    for r in rows:
        r = dict(r)
        if isinstance(r.get("objections"), (list, tuple)):
            r["objections"] = json.dumps(list(r["objections"]))
        prepared.append(tuple(r.get(c) for c in cols))
    with get_conn() as conn:
        conn.executemany(
            f"INSERT INTO calls ({', '.join(cols)}) VALUES ({', '.join('?' * len(cols))})",
            prepared,
        )


def calls_df(rep_name: str | None = None, days: int | None = None) -> pd.DataFrame:
    """All calls as a DataFrame, newest first, with parsed datetime and
    `objections` decoded back to a Python list."""
    query = "SELECT * FROM calls"
    where, params = [], []
    if rep_name:
        where.append("rep_name = ?")
        params.append(rep_name)
    if days:
        where.append("call_time >= datetime('now', ?)")
        params.append(f"-{int(days)} days")
    if where:
        query += " WHERE " + " AND ".join(where)
    query += " ORDER BY call_time DESC"
    with get_conn() as conn:
        df = pd.read_sql_query(query, conn, params=params)
    if not df.empty:
        df["call_time"] = pd.to_datetime(df["call_time"])
        df["objections"] = df["objections"].apply(lambda s: json.loads(s) if s else [])
    return df


def rep_names() -> list[str]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT rep_name, COUNT(*) AS n FROM calls GROUP BY rep_name ORDER BY n DESC"
        ).fetchall()
    return [r["rep_name"] for r in rows]


def save_coach_note(rep_name: str, note: str, author: str = "Manager") -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO coach_notes (rep_name, note, author) VALUES (?, ?, ?)",
            (rep_name, note.strip(), author),
        )


def coach_notes(rep_name: str) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT note, author, created_at FROM coach_notes "
            "WHERE rep_name = ? ORDER BY created_at DESC",
            (rep_name,),
        ).fetchall()
    return [dict(r) for r in rows]
