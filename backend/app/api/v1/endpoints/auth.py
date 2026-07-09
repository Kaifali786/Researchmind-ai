"""
Authentication API endpoints.

Routes:
    POST /register  — Create a new user account.
    POST /login     — Authenticate and obtain JWT tokens.
    GET  /me        — Retrieve the authenticated user's profile.
    POST /refresh   — Exchange a refresh token for a new token pair.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    RefreshTokenRequest,
    Token,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    responses={
        409: {"description": "Email or username already exists."},
    },
)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Register a new user account.

    Validates email / username uniqueness, hashes the password, and
    returns the newly created user profile.

    Args:
        user_data: Registration payload with email, username, password.
        db: Async database session.

    Returns:
        The created user profile.

    Raises:
        HTTPException 409: Duplicate email or username.
    """
    auth_service = AuthService(db)
    return await auth_service.register(user_data)


@router.post(
    "/login",
    response_model=Token,
    summary="Log in and obtain tokens",
    responses={
        401: {"description": "Invalid credentials."},
        403: {"description": "Account deactivated."},
    },
)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    Authenticate with email and password to receive a JWT token pair.

    Args:
        credentials: Login payload with email and password.
        db: Async database session.

    Returns:
        Access and refresh tokens.

    Raises:
        HTTPException 401: Invalid email or password.
        HTTPException 403: Account deactivated.
    """
    auth_service = AuthService(db)
    return await auth_service.login(credentials)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    responses={
        401: {"description": "Not authenticated."},
    },
)
async def get_me(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Return the profile of the currently authenticated user.

    Requires a valid JWT access token in the Authorization header.

    Args:
        current_user: Injected by the authentication dependency.

    Returns:
        The user profile.
    """
    return current_user


@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh tokens",
    responses={
        401: {"description": "Invalid or expired refresh token."},
    },
)
async def refresh_token(
    body: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    Exchange a valid refresh token for a new access/refresh token pair.

    The old refresh token is effectively consumed — a brand-new pair
    is always issued.

    Args:
        body: Contains the refresh token.
        db: Async database session.

    Returns:
        A fresh token pair.

    Raises:
        HTTPException 401: Invalid or expired refresh token.
    """
    auth_service = AuthService(db)
    return await auth_service.refresh_tokens(body.refresh_token)
