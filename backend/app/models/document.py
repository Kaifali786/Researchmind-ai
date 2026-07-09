"""
Document and DocumentChunk ORM models.

- **Document**: Represents an uploaded research paper / file.
- **DocumentChunk**: Stores pre-processed text chunks for retrieval-augmented
  generation (RAG). Each chunk belongs to exactly one document.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

import enum


class DocumentStatus(str, enum.Enum):
    """Processing status of an uploaded document."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(Base):
    """
    An uploaded research document belonging to a user.

    Attributes:
        id: Primary key UUID.
        user_id: Foreign key to the owning user.
        title: Human-readable title (defaults to filename).
        filename: Original filename on the client machine.
        file_type: MIME type or extension (e.g. ``application/pdf``).
        file_path: Server-side storage path.
        file_size: File size in bytes.
        abstract: Extracted or user-supplied abstract.
        metadata_: Arbitrary JSON metadata (authors, DOI, etc.).
        status: Processing pipeline status.
        page_count: Number of pages (populated after processing).
        uploaded_at: Upload timestamp.
        processed_at: Timestamp when processing completed / failed.
    """

    __tablename__ = "documents"

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
    title: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )
    filename: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )
    file_type: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )
    file_path: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
    )
    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    abstract: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata",
        JSON,
        nullable=True,
        default=dict,
    )
    status: Mapped[DocumentStatus] = mapped_column(
        SAEnum(DocumentStatus, name="document_status", create_constraint=True),
        default=DocumentStatus.PENDING,
        nullable=False,
        index=True,
    )
    page_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ── Relationships ────────────────────────────────────────────────
    owner: Mapped["User"] = relationship(  # noqa: F821
        "User",
        back_populates="documents",
    )
    chunks: Mapped[list["DocumentChunk"]] = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    notes: Mapped[list["Note"]] = relationship(  # noqa: F821
        "Note",
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    citations: Mapped[list["Citation"]] = relationship(  # noqa: F821
        "Citation",
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Document id={self.id} title={self.title!r}>"


class DocumentChunk(Base):
    """
    A text chunk extracted from a Document for vector search / RAG.

    Attributes:
        id: Primary key UUID.
        document_id: Parent document FK.
        chunk_index: Ordering index within the document.
        content: The raw text content of this chunk.
        page_number: Source page number (if applicable).
        section: Section heading the chunk belongs to (if any).
        embedding_id: Reference to an external vector store embedding.
    """

    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    page_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    section: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
    )
    embedding_id: Mapped[str | None] = mapped_column(
        String(256),
        nullable=True,
    )

    # ── Relationships ────────────────────────────────────────────────
    document: Mapped["Document"] = relationship(
        "Document",
        back_populates="chunks",
    )

    def __repr__(self) -> str:
        return f"<DocumentChunk id={self.id} index={self.chunk_index}>"
