"""
Note repository — data-access layer for the ``notes`` table.

Provides user-scoped queries, document-scoped filtering, and tag search.
"""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.note import Note
from app.repositories.base import BaseRepository


class NoteRepository(BaseRepository[Note]):
    """
    Async repository for Note CRUD and look-ups.

    All multi-record queries are scoped to a specific user.
    """

    model = Note

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialise the note repository.

        Args:
            db: Active async database session.
        """
        super().__init__(db)

    async def get_by_user(
        self,
        user_id: UUID,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Note]:
        """
        Fetch all notes belonging to a specific user.

        Args:
            user_id: The owning user's UUID.
            skip: Pagination offset.
            limit: Page size.

        Returns:
            List of ``Note`` instances ordered by creation date (newest first).
        """
        result = await self.db.execute(
            select(Note)
            .where(Note.user_id == user_id)
            .order_by(Note.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_user(self, user_id: UUID) -> int:
        """
        Count notes belonging to a specific user.

        Args:
            user_id: The owning user's UUID.

        Returns:
            Integer note count.
        """
        result = await self.db.execute(
            select(func.count())
            .select_from(Note)
            .where(Note.user_id == user_id)
        )
        return result.scalar_one()

    async def get_by_document(
        self,
        document_id: UUID,
        user_id: UUID,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Note]:
        """
        Fetch notes attached to a specific document, scoped to the user.

        Args:
            document_id: The document's UUID.
            user_id: The owning user's UUID.
            skip: Pagination offset.
            limit: Page size.

        Returns:
            List of ``Note`` instances.
        """
        result = await self.db.execute(
            select(Note)
            .where(Note.document_id == document_id, Note.user_id == user_id)
            .order_by(Note.page_number.asc().nulls_last(), Note.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_user_note(
        self,
        note_id: UUID,
        user_id: UUID,
    ) -> Note | None:
        """
        Fetch a single note ensuring ownership.

        Args:
            note_id: Note primary key.
            user_id: Expected owner.

        Returns:
            The ``Note`` if found and owned by the user, else ``None``.
        """
        result = await self.db.execute(
            select(Note).where(Note.id == note_id, Note.user_id == user_id)
        )
        return result.scalars().first()

    async def delete_user_note(
        self,
        note_id: UUID,
        user_id: UUID,
    ) -> bool:
        """
        Delete a note only if it belongs to the specified user.

        Args:
            note_id: Note primary key.
            user_id: Expected owner.

        Returns:
            ``True`` if deleted, ``False`` if not found or not owned.
        """
        note = await self.get_user_note(note_id, user_id)
        if note is None:
            return False
        await self.db.delete(note)
        await self.db.commit()
        return True
