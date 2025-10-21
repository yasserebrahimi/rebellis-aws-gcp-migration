"""
Core Security Utilities
Handles JWT encoding/decoding, password hashing, and validation logic.
"""

import jwt
import bcrypt
import datetime
from typing import Optional, Dict, Any
from src.core.config import settings


# === Password Hashing ===

def hash_password(password: str) -> str:
    """Return bcrypt hash for a plain-text password."""
    salt = bcrypt.gensalt(rounds=settings.PASSWORD_HASH_ROUNDS)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Check if provided password matches hashed value."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


# === JWT Token Handling ===

def create_access_token(data: Dict[str, Any]) -> str:
    """Create short-lived (access) JWT token."""
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode, settings.JWT_SECRET_KEY.get_secret_value(), algorithm=settings.JWT_ALGORITHM
    )


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create long-lived (refresh) JWT token."""
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(
        days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(
        to_encode, settings.JWT_SECRET_KEY.get_secret_value(), algorithm=settings.JWT_ALGORITHM
    )


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token format")
