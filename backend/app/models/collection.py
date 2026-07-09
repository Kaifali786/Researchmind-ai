"""
Collection ORM model and association table.

Collections allow users to organise documents into named groups
(e.g. "Machine Learning Papers", "Thesis References").
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# ── Many-to-Many association table ───────────────────────────────────────────

collection_documents = Table(
    "collection_documents",
    Base.metadata,
    Column(
        "collection_id",
        UUID(as_uuid=True),
        ForeignKey("collections.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "document_id",
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Collection(Base):
    """
    A named group of documents belonging to a user.

    Attributes:
        id: Primary key UUID.
        user_id: FK to the owning user.
        name: Collection display name.
        description: Optional longer description.
        created_at: Creation timestamp.
    """

    __tablename__ = "collections"

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
    name: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ── Relationships ────────────────────────────────────────────────
    user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        back_populates="collections",
    )
    documents: Mapped[list["Document"]] = relationship(  # noqa: F821
        "Document",
        secondary=collection_documents,
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Collection id={self.id} name={self.name!r}>"
