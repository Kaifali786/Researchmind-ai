"""
FastAPI dependency injection utilities.

Provides reusable ``Depends(...)`` callables for:
- Database sessions
- Authenticated user extraction from JWT bearer tokens
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.services.auth_service import AuthService

# ── Security scheme ──────────────────────────────────────────────────────────

_bearer_scheme = HTTPBearer(
    scheme_name="JWT",
    description="Paste a valid JWT access token (without the 'Bearer ' prefix).",
    auto_error=True,
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    FastAPI dependency that extracts and validates the current user
    from the ``Authorization: Bearer <token>`` header.

    Args:
        credentials: Parsed bearer credentials injected by FastAPI.
        db: Async database session.

    Returns:
        The authenticated ``User`` ORM instance.

    Raises:
        HTTPException 401: If the token is missing, invalid, expired,
                           or the user does not exist.
        HTTPException 403: If the user account is deactivated.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    auth_service = AuthService(db)
    return await auth_service.get_current_user(credentials.credentials)


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency that returns the current user only if the account is active.

    Args:
        current_user: Injected via ``get_current_user``.

    Returns:
        The authenticated, active ``User``.

    Raises:
        HTTPException 403: If the account is deactivated.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )
    return current_user
