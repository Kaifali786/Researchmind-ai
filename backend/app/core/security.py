"""
Security utilities for JWT token management and password hashing.

Provides:
- Password hashing and verification with bcrypt via passlib.
- JWT access / refresh token creation and verification with python-jose.
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

# ── Password hashing context ────────────────────────────────────────────────

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    Args:
        plain_password: The user-supplied password in plain text.

    Returns:
        A bcrypt hash string safe for database storage.
    """
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a stored bcrypt hash.

    Args:
        plain_password: The password attempt from the client.
        hashed_password: The hash stored in the database.

    Returns:
        ``True`` if the password matches, ``False`` otherwise.
    """
    return _pwd_context.verify(plain_password, hashed_password)


# ── JWT token helpers ────────────────────────────────────────────────────────


def create_access_token(
    subject: str | UUID,
    extra_claims: dict | None = None,
) -> str:
    """
    Create a short-lived JWT access token.

    Args:
        subject: The token subject – typically the user's UUID.
        extra_claims: Optional additional claims to embed in the payload.

    Returns:
        An encoded JWT string.
    """
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload: dict = {
        "sub": str(subject),
        "iat": now,
        "exp": expire,
        "type": "access",
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str | UUID) -> str:
    """
    Create a long-lived JWT refresh token.

    Args:
        subject: The token subject – typically the user's UUID.

    Returns:
        An encoded JWT string with ``type=refresh``.
    """
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    payload: dict = {
        "sub": str(subject),
        "iat": now,
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict | None:
    """
    Decode and verify a JWT token.

    Args:
        token: The raw JWT string from the ``Authorization`` header.

    Returns:
        The decoded payload as a ``dict``, or ``None`` if the token is
        invalid, expired, or otherwise malformed.
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        return None


def verify_access_token(token: str) -> dict | None:
    """
    Decode a JWT and ensure it is an *access* token.

    Args:
        token: The raw JWT string.

    Returns:
        The decoded payload ``dict`` when valid **and** ``type == "access"``,
        otherwise ``None``.
    """
    payload = decode_token(token)
    if payload is None:
        return None
    if payload.get("type") != "access":
        return None
    return payload


def verify_refresh_token(token: str) -> dict | None:
    """
    Decode a JWT and ensure it is a *refresh* token.

    Args:
        token: The raw JWT string.

    Returns:
        The decoded payload ``dict`` when valid **and** ``type == "refresh"``,
        otherwise ``None``.
    """
    payload = decode_token(token)
    if payload is None:
        return None
    if payload.get("type") != "refresh":
        return None
    return payload
