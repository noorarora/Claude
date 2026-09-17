import os
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

DEFAULT_DATABASE = Path("phishguard.db")


def database_path() -> Path:
    return Path(os.getenv("PHISHGUARD_DATABASE", str(DEFAULT_DATABASE)))


@contextmanager
def connection() -> Iterator[sqlite3.Connection]:
    database = sqlite3.connect(database_path())
    database.row_factory = sqlite3.Row
    try:
        yield database
        database.commit()
    finally:
        database.close()


def initialise_database() -> None:
    with connection() as database:
        database.execute(
            """
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                risk_score INTEGER NOT NULL,
                confidence REAL NOT NULL,
                verdict TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def save_analysis(text: str, risk_score: int, confidence: float, verdict: str) -> sqlite3.Row:
    with connection() as database:
        cursor = database.execute(
            "INSERT INTO analyses (text, risk_score, confidence, verdict) VALUES (?, ?, ?, ?)",
            (text, risk_score, confidence, verdict),
        )
        return database.execute(
            "SELECT * FROM analyses WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()


def recent_analyses(limit: int = 10) -> list[sqlite3.Row]:
    with connection() as database:
        return database.execute(
            "SELECT * FROM analyses ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()

