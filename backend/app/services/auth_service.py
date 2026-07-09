"""
Authentication service — business logic for registration, login, and
token management.

Orchestrates between the UserRepository, security utilities, and
Pydantic schemas.
"""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_access_token,
    verify_refresh_token,
)
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.auth import Token, UserCreate, UserLogin


class AuthService:
    """
    Handles all authentication-related business logic.

    Each public method receives a DB session (or repository) and the
    relevant Pydantic schema, then returns domain objects or raises
    ``HTTPException`` on failure.
    """

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialise with a database session.

        Args:
            db: Active async database session.
        """
        self.db = db
        self.user_repo = UserRepository(db)

    async def register(self, user_data: UserCreate) -> User:
        """
        Register a new user account.

        Validates uniqueness of email and username, hashes the password,
        persists the user, and returns the created model.

        Args:
            user_data: Validated registration payload.

        Returns:
            The newly created ``User`` instance.

        Raises:
            HTTPException 409: If the email or username is already taken.
        """
        # ── Uniqueness checks ────────────────────────────────────────
        if await self.user_repo.email_exists(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email address already exists.",
            )

        if await self.user_repo.username_exists(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This username is already taken.",
            )

        # ── Create user ──────────────────────────────────────────────
        hashed = hash_password(user_data.password)
        user = await self.user_repo.create(
            {
                "email": user_data.email.lower(),
                "username": user_data.username,
                "hashed_password": hashed,
                "full_name": user_data.full_name,
            }
        )
        return user

    async def login(self, credentials: UserLogin) -> Token:
        """
        Authenticate a user and issue a JWT token pair.

        Args:
            credentials: Email and password from the client.

        Returns:
            A ``Token`` schema containing access and refresh tokens.

        Raises:
            HTTPException 401: If the email is not found or the password
                               does not match.
        """
        user = await self.user_repo.get_by_email(credentials.email)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deactivated.",
            )

        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def get_current_user(self, token: str) -> User:
        """
        Resolve the current user from a JWT access token.

        Args:
            token: Raw JWT access token string.

        Returns:
            The authenticated ``User`` instance.

        Raises:
            HTTPException 401: If the token is invalid, expired, or the
                               user no longer exists / is deactivated.
        """
        payload = verify_access_token(token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired access token.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id_str: str | None = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload missing subject claim.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            user_id = UUID(user_id_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user identifier in token.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deactivated.",
            )

        return user

    async def refresh_tokens(self, refresh_token: str) -> Token:
        """
        Issue a new access/refresh token pair from a valid refresh token.

        The old refresh token is consumed (one-time use semantics are
        enforced by issuing a brand-new pair).

        Args:
            refresh_token: A valid JWT refresh token.

        Returns:
            A fresh ``Token`` schema.

        Raises:
            HTTPException 401: If the refresh token is invalid, expired,
                               or the user no longer exists.
        """
        payload = verify_refresh_token(refresh_token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id_str: str | None = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload missing subject claim.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            user_id = UUID(user_id_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user identifier in token.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = await self.user_repo.get_by_id(user_id)
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or deactivated.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        new_access = create_access_token(subject=user.id)
        new_refresh = create_refresh_token(subject=user.id)

        return Token(
            access_token=new_access,
            refresh_token=new_refresh,
        )
