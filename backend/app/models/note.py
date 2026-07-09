"""
Note ORM model.

Users can attach notes to documents (or create standalone notes).
Tags are stored as a JSON array for flexible filtering.
"""

import uuid
import enum
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class NoteType(str, enum.Enum):
    """Categorises how a note was created."""

    HIGHLIGHT = "highlight"
    ANNOTATION = "annotation"
    GENERAL = "general"
    SUMMARY = "summary"


class Note(Base):
    """
    A user-created note, optionally linked to a document page.

    Attributes:
        id: Primary key UUID.
        user_id: FK to the note author.
        document_id: FK to an associated document (nullable for standalone notes).
        content: The note body (Markdown supported).
        note_type: Categorisation of the note.
        page_number: Page reference inside the linked document.
        tags: JSON array of string tags for filtering.
        created_at: Creation timestamp.
        updated_at: Last-edit timestamp.
    """

    __tablename__ = "notes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    note_type: Mapped[NoteType] = mapped_column(
        SAEnum(NoteType, name="note_type", create_constraint=True),
        default=NoteType.GENERAL,
        nullable=False,
    )
    page_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    tags: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
        default=list,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ── Relationships ────────────────────────────────────────────────
    user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        back_populates="notes",
    )
    document: Mapped["Document | None"] = relationship(  # noqa: F821
        "Document",
        back_populates="notes",
    )

    def __repr__(self) -> str:
        return f"<Note id={self.id} type={self.note_type.value}>"
