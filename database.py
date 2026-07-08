"""SQLite helper functions for the AI Code Reviewer backend.

This file is intentionally small and dependency-free so the internship project
can satisfy database requirements without changing the existing frontend code.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

# Define the base directory and database file path
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "ai_code_reviewer.db"


def get_connection() -> sqlite3.Connection:
    """
    Create a SQLite connection with rows accessible like dictionaries.
    - check_same_thread=False allows usage across threads.
    - row_factory=sqlite3.Row makes query results behave like dicts.
    """
    connection = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    """
    Initialize the database by creating required tables if they don't exist.
    - users table stores account info.
    - api_logs table stores logs for API requests.
    """
    with get_connection() as connection:
        # Create users table
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
        # Create API logs table
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
    """
    Convert a SQLite Row object into a Python dictionary.
    Returns None if the row is None.
    """
    if row is None:
        return None
    return dict(row)


def public_user(row: sqlite3.Row | dict[str, Any]) -> dict[str, Any]:
    """
    Convert a user row into a public dictionary format.
    Removes sensitive fields like password_hash.
    """
    data = dict(row)
    data.pop("password_hash", None)  # Remove password hash for security
    return {
        "id": data.get("id"),
        "email": data.get("email"),
        "profileImage": data.get("profile_image"),
        "createdAt": data.get("created_at"),
    }


def create_user(
    email: str,
    password_hash: str,
    profile_image: str | None = None
) -> dict[str, Any] | None:
    """
    Insert a new user into the database.
    Returns the created user in public format, or None if insertion fails.
    """
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
        if user_id is None:
            return None

    user = get_user_by_id(int(user_id))
    return public_user(user) if user else None


def get_user_by_email(email: str) -> sqlite3.Row | None:
    """
    Fetch a user row by email.
    Case-insensitive match using lower().
    """
    with get_connection() as connection:
        return connection.execute(
            "SELECT * FROM users WHERE lower(email) = lower(?)",
            (email,),
        ).fetchone()


def get_user_by_id(user_id: int) -> sqlite3.Row | None:
    """
    Fetch a user row by ID.
    Returns None if no user is found.
    """
    with get_connection() as connection:
        return connection.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()


def list_users() -> list[dict[str, Any]]:
    """
    Fetch all users ordered by creation date (latest first).
    Returns a list of public user dictionaries.
    """
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM users ORDER BY created_at DESC"
        ).fetchall()
    return [public_user(row) for row in rows if row is not None]


def update_user_profile_image(
    user_id: int,
    profile_image: str | None
) -> dict[str, Any] | None:
    """
    Update the profile image of a user by ID.
    Returns the updated user in public format, or None if not found.
    """
    with get_connection() as connection:
        connection.execute(
            "UPDATE users SET profile_image = ? WHERE id = ?",
            (profile_image, user_id),
        )
        connection.commit()

    user = get_user_by_id(user_id)
    return public_user(user) if user else None


def insert_api_log(
    level: str,
    logger_name: str | None,
    message: str,
    method: str | None = None,
    path: str | None = None,
    status_code: int | None = None,
) -> None:
    """
    Insert a new API log entry into the database.
    Used by the logging framework handler.
    """
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
    """
    Fetch recent API logs with a safe limit (1–200).
    Returns a list of log dictionaries with renamed keys for frontend use.
    """
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
