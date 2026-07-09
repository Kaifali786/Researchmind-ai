"""
User ORM model.

Stores registered users with hashed credentials and profile metadata.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    """
    Represents a registered user of the ResearchMind AI platform.

    Attributes:
        id: Primary key UUID.
        email: Unique email address used for login.
        username: Unique display name.
        hashed_password: Bcrypt hash of the user's password.
        full_name: Optional real name.
        is_active: Soft-delete / account-disable flag.
        created_at: Timestamp of account creation.
        updated_at: Timestamp of the last profile update.
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        nullable=False,
        index=True,
    )
    username: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
    )
    full_name: Mapped[str | None] = mapped_column(
        String(256),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
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
    documents: Mapped[list["Document"]] = relationship(  # noqa: F821
        "Document",
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    chat_sessions: Mapped[list["ChatSession"]] = relationship(  # noqa: F821
        "ChatSession",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    notes: Mapped[list["Note"]] = relationship(  # noqa: F821
        "Note",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    collections: Mapped[list["Collection"]] = relationship(  # noqa: F821
        "Collection",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"
