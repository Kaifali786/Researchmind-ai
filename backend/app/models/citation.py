"""
Citation ORM model.

Stores generated bibliographic citations in various formats (APA, MLA, etc.)
for documents in the system.
"""

import uuid
import enum
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Text,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CitationFormat(str, enum.Enum):
    """Supported bibliographic citation formats."""

    APA = "apa"
    MLA = "mla"
    CHICAGO = "chicago"
    IEEE = "ieee"
    HARVARD = "harvard"
    BIBTEX = "bibtex"


class Citation(Base):
    """
    A bibliographic citation generated for a document.

    Attributes:
        id: Primary key UUID.
        document_id: FK to the source document.
        format: Citation style (APA, MLA, etc.).
        citation_text: Fully rendered citation string.
        metadata_: JSON with structured citation fields (authors, year, etc.).
        created_at: Creation timestamp.
    """

    __tablename__ = "citations"

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
    format: Mapped[CitationFormat] = mapped_column(
        SAEnum(CitationFormat, name="citation_format", create_constraint=True),
        nullable=False,
    )
    citation_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata",
        JSON,
        nullable=True,
        default=dict,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ── Relationships ────────────────────────────────────────────────
    document: Mapped["Document"] = relationship(  # noqa: F821
        "Document",
        back_populates="citations",
    )

    def __repr__(self) -> str:
        return f"<Citation id={self.id} format={self.format.value}>"
