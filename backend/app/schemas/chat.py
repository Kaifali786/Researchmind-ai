"""
Pydantic v2 schemas for chat endpoints.

Covers session creation, message submission, and read-back responses.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ── Request schemas ──────────────────────────────────────────────────────────


class ChatCreate(BaseModel):
    """Schema for creating a new chat session."""

    title: str = Field(
        default="New Chat",
        max_length=256,
        description="Session title.",
        examples=["Literature Review Discussion"],
    )


class MessageCreate(BaseModel):
    """Schema for sending a message in a chat session."""

    content: str = Field(
        ...,
        min_length=1,
        max_length=32_000,
        description="Message content.",
        examples=["Summarise the key findings of this paper."],
    )
    role: str = Field(
        default="user",
        description="Message sender role.",
        examples=["user"],
    )


# ── Response schemas ─────────────────────────────────────────────────────────


class MessageResponse(BaseModel):
    """Read-only representation of a single chat message."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    session_id: UUID
    role: str
    content: str
    citations: dict | None = None
    confidence_score: float | None = None
    created_at: datetime


class ChatResponse(BaseModel):
    """Read-only representation of a chat session with its messages."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    title: str
    created_at: datetime
    messages: list[MessageResponse] = Field(default_factory=list)


class ChatListResponse(BaseModel):
    """Lightweight list of chat sessions (without full message history)."""

    sessions: list[ChatResponse]
    total: int
