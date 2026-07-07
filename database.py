"""SQLite helper functions for the AI Code Reviewer backend.

This file is intentionally small and dependency-free so the internship project
can satisfy database requirements without changing the existing frontend code.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "ai_code_reviewer.db"


def get_connection() -> sqlite3.Connection:
    """Create a SQLite connection with rows accessible like dictionaries."""
    connection = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    """Create the required tables if they do not already exist."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                profile_image TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS api_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL,
                logger_name TEXT,
                message TEXT NOT NULL,
                method TEXT,
                path TEXT,
                status_code INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return dict(row)


def public_user(row: sqlite3.Row | dict[str, Any] | None) -> dict[str, Any] | None:
    """Return user data without exposing the stored password hash."""
    if row is None:
        return None
    data = dict(row)
    data.pop("password_hash", None)
    return {
        "id": data.get("id"),
        "email": data.get("email"),
        "profileImage": data.get("profile_image"),
        "createdAt": data.get("created_at"),
    }


def create_user(email: str, password_hash: str, profile_image: str | None = None) -> dict[str, Any]:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO users (email, password_hash, profile_image)
            VALUES (?, ?, ?)
            """,
            (email, password_hash, profile_image),
        )
        connection.commit()
        user_id = cursor.lastrowid

    user = get_user_by_id(int(user_id))
    return public_user(user)  # type: ignore[return-value]


def get_user_by_email(email: str) -> sqlite3.Row | None:
    with get_connection() as connection:
        return connection.execute(
            "SELECT * FROM users WHERE lower(email) = lower(?)",
            (email,),
        ).fetchone()


def get_user_by_id(user_id: int) -> sqlite3.Row | None:
    with get_connection() as connection:
        return connection.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()


def list_users() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM users ORDER BY created_at DESC"
        ).fetchall()
    return [public_user(row) for row in rows if row is not None]


def update_user_profile_image(user_id: int, profile_image: str | None) -> dict[str, Any] | None:
    with get_connection() as connection:
        connection.execute(
            "UPDATE users SET profile_image = ? WHERE id = ?",
            (profile_image, user_id),
        )
        connection.commit()

    return public_user(get_user_by_id(user_id))


def insert_api_log(
    level: str,
    logger_name: str | None,
    message: str,
    method: str | None = None,
    path: str | None = None,
    status_code: int | None = None,
) -> None:
    """Write one log row into SQLite. Used by the logging framework handler."""
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO api_logs (level, logger_name, message, method, path, status_code)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (level, logger_name, message, method, path, status_code),
        )
        connection.commit()


def get_api_logs(limit: int = 50) -> list[dict[str, Any]]:
    safe_limit = max(1, min(limit, 200))
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, level, logger_name AS loggerName, message, method, path,
                   status_code AS statusCode, created_at AS createdAt
            FROM api_logs
            ORDER BY id DESC
            LIMIT ?
            """,
            (safe_limit,),
        ).fetchall()
    return [dict(row) for row in rows]
