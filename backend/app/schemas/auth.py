"""
Pydantic v2 schemas for authentication endpoints.

Covers user registration, login, token responses, and user profile output.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ── Request schemas ──────────────────────────────────────────────────────────


class UserCreate(BaseModel):
    """Schema for new user registration."""

    email: EmailStr = Field(
        ...,
        description="A valid, unique email address.",
        examples=["alice@example.com"],
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=64,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Unique username (letters, digits, hyphens, underscores).",
        examples=["alice_researcher"],
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Strong password (at least 8 characters).",
        examples=["S3cur3Pa$$word!"],
    )
    full_name: str | None = Field(
        None,
        max_length=256,
        description="Optional full name.",
        examples=["Alice Johnson"],
    )


class UserLogin(BaseModel):
    """Schema for email + password login."""

    email: EmailStr = Field(
        ...,
        description="Registered email address.",
        examples=["alice@example.com"],
    )
    password: str = Field(
        ...,
        description="Account password.",
        examples=["S3cur3Pa$$word!"],
    )


class RefreshTokenRequest(BaseModel):
    """Schema for requesting a new access token via a refresh token."""

    refresh_token: str = Field(
        ...,
        description="A valid JWT refresh token.",
    )


# ── Response schemas ─────────────────────────────────────────────────────────


class UserResponse(BaseModel):
    """Public user profile returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    username: str
    full_name: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    """JWT token pair returned after login or token refresh."""

    access_token: str = Field(
        ...,
        description="Short-lived JWT access token.",
    )
    refresh_token: str = Field(
        ...,
        description="Long-lived JWT refresh token.",
    )
    token_type: str = Field(
        default="bearer",
        description="Token scheme (always 'bearer').",
    )


class TokenPayload(BaseModel):
    """Decoded JWT payload used internally."""

    sub: str = Field(..., description="Subject (user UUID).")
    exp: int = Field(..., description="Expiration timestamp (epoch seconds).")
    iat: int = Field(..., description="Issued-at timestamp.")
    type: str = Field(..., description="Token type ('access' or 'refresh').")
