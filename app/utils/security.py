"""
Security utilities for authentication and authorization.

This module provides common security functions that can be used
across different authentication strategies. Uncomment and implement
the functions you need for your specific project.
"""

import hashlib
import secrets


def generate_random_string(length: int = 32) -> str:
    """
    Generate a cryptographically secure random string.

    Args:
        length: Length of the random string.

    Returns:
        str: Random string.
    """
    return secrets.token_urlsafe(length)


def hash_string(value: str) -> str:
    """
    Hash a string using SHA-256.

    Args:
        value: String to hash.

    Returns:
        str: Hexadecimal hash.
    """
    return hashlib.sha256(value.encode()).hexdigest()


# Add your authentication/security functions here:
#
# Example: Password hashing with bcrypt
# from passlib.context import CryptContext
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#
# def hash_password(password: str) -> str:
#     """Hash a password."""
#     return pwd_context.hash(password)
#
# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     """Verify a password against its hash."""
#     return pwd_context.verify(plain_password, hashed_password)
#
# Example: JWT token handling
# import jwt
# from datetime import datetime, timedelta, timezone
#
# def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
#     """Create a JWT access token."""
#     # Implementation here
#     pass
#
# def decode_access_token(token: str) -> dict | None:
#     """Decode a JWT access token."""
#     # Implementation here
#     pass
