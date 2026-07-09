"""
Pydantic v2 schemas for note endpoints.

Covers creation, partial update, and read-back.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ── Request schemas ──────────────────────────────────────────────────────────


class NoteCreate(BaseModel):
    """Schema for creating a new note."""

    document_id: UUID | None = Field(
        None,
        description="Optional FK to the document this note is attached to.",
    )
    content: str = Field(
        ...,
        min_length=1,
        max_length=50_000,
        description="Note body (Markdown supported).",
        examples=["Key insight: transformer attention scales quadratically."],
    )
    note_type: str = Field(
        default="general",
        description="Note category: highlight | annotation | general | summary.",
        examples=["annotation"],
    )
    page_number: int | None = Field(
        None,
        ge=1,
        description="Page reference within the linked document.",
    )
    tags: list[str] | None = Field(
        None,
        description="List of string tags for filtering.",
        examples=[["transformers", "attention"]],
    )


class NoteUpdate(BaseModel):
    """
    Schema for partially updating a note.

    All fields are optional – only supplied fields are modified.
    """

    content: str | None = Field(
        None,
        min_length=1,
        max_length=50_000,
        description="Updated note body.",
    )
    note_type: str | None = Field(
        None,
        description="Updated note category.",
    )
    page_number: int | None = Field(
        None,
        ge=1,
        description="Updated page reference.",
    )
    tags: list[str] | None = Field(
        None,
        description="Replacement tag list.",
    )


# ── Response schemas ─────────────────────────────────────────────────────────


class NoteResponse(BaseModel):
    """Read-only representation of a note."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    document_id: UUID | None = None
    content: str
    note_type: str
    page_number: int | None = None
    tags: list[str] | None = None
    created_at: datetime
    updated_at: datetime


class NoteListResponse(BaseModel):
    """Paginated list of notes."""

    notes: list[NoteResponse]
    total: int
