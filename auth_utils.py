"""Beginner-friendly password hashing utilities.
"""

from __future__ import annotations

import hashlib   # Provides SHA-256 hashing
import hmac      # Provides secure comparison of hashes
import secrets   # Provides cryptographically secure random values


def hash_password(password: str) -> str:
    """
    Hash a password using SHA-256 with a random salt.

    Steps:
    1. Generate a random salt (unique string for each password).
    2. Concatenate salt + password.
    3. Hash the result using SHA-256.
    4. Store as "salt$hash" so we can verify later.

    Example stored value:
    "a1b2c3d4...$5f6g7h8..."
    """
    # Generate a random salt (32 hex characters = 16 bytes)
    salt = secrets.token_hex(16)

    # Hash the salt + password together
    password_hash = hashlib.sha256(f"{salt}{password}".encode("utf-8")).hexdigest()

    # Return combined salt and hash, separated by "$"
    return f"{salt}${password_hash}"


def verify_password(password: str, stored_value: str) -> bool:
    """
    Verify a plain password against the stored "salt$hash" value.

    Steps:
    1. Split stored value into salt and expected hash.
    2. Recompute hash using salt + provided password.
    3. Compare securely using hmac.compare_digest (prevents timing attacks).

    Returns:
    - True if password matches.
    - False if password is invalid or stored value is malformed.
    """
    try:
        # Extract salt and hash from stored value
        salt, expected_hash = stored_value.split("$", 1)
    except ValueError:
        # If stored value is not in "salt$hash" format
        return False

    # Recompute hash with the provided password
    actual_hash = hashlib.sha256(f"{salt}{password}".encode("utf-8")).hexdigest()

    # Securely compare expected vs actual hash
    return hmac.compare_digest(actual_hash, expected_hash)
