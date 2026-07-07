"""Beginner-friendly password hashing utilities."""

from __future__ import annotations

import hashlib
import hmac
import secrets


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with a random salt.

    This is good for an internship demo and avoids extra dependencies.
    For a real production system, use bcrypt or Argon2.
    """
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256(f"{salt}{password}".encode("utf-8")).hexdigest()
    return f"{salt}${password_hash}"


def verify_password(password: str, stored_value: str) -> bool:
    """Verify a plain password against the stored salt$hash value."""
    try:
        salt, expected_hash = stored_value.split("$", 1)
    except ValueError:
        return False

    actual_hash = hashlib.sha256(f"{salt}{password}".encode("utf-8")).hexdigest()
    return hmac.compare_digest(actual_hash, expected_hash)
