"""
Document repository — data-access layer for the ``documents`` table.

Provides user-scoped queries and status-based filtering.
"""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentStatus
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    """
    Async repository for Document CRUD and look-ups.

    All multi-record queries are scoped to a specific user to enforce
    data-access isolation.
    """

    model = Document

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialise the document repository.

        Args:
            db: Active async database session.
        """
        super().__init__(db)

    async def get_by_user(
        self,
        user_id: UUID,
        *,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Document]:
        """
        Fetch all documents belonging to a specific user.

        Args:
            user_id: The owning user's UUID.
            skip: Pagination offset.
            limit: Page size.

        Returns:
            List of ``Document`` instances ordered by upload date (newest first).
        """
        result = await self.db.execute(
            select(Document)
            .where(Document.user_id == user_id)
            .order_by(Document.uploaded_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_user(self, user_id: UUID) -> int:
        """
        Count documents belonging to a specific user.

        Args:
            user_id: The owning user's UUID.

        Returns:
            Integer document count.
        """
        result = await self.db.execute(
            select(func.count())
            .select_from(Document)
            .where(Document.user_id == user_id)
        )
        return result.scalar_one()

    async def get_user_document(
        self,
        document_id: UUID,
        user_id: UUID,
    ) -> Document | None:
        """
        Fetch a single document ensuring it belongs to the given user.

        This prevents horizontal privilege escalation — a user cannot read
        another user's document even if they know the UUID.

        Args:
            document_id: Document primary key.
            user_id: Expected owner.

        Returns:
            The ``Document`` if found and owned by the user, else ``None``.
        """
        result = await self.db.execute(
            select(Document).where(
                Document.id == document_id,
                Document.user_id == user_id,
            )
        )
        return result.scalars().first()

    async def get_by_status(
        self,
        status: DocumentStatus,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Document]:
        """
        Fetch documents filtered by processing status.

        Useful for background workers that pick up ``PENDING`` documents.

        Args:
            status: Target processing status.
            skip: Pagination offset.
            limit: Page size.

        Returns:
            List of matching documents.
        """
        result = await self.db.execute(
            select(Document)
            .where(Document.status == status)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def delete_user_document(
        self,
        document_id: UUID,
        user_id: UUID,
    ) -> bool:
        """
        Delete a document only if it belongs to the specified user.

        Args:
            document_id: Document primary key.
            user_id: Expected owner.

        Returns:
            ``True`` if the document was found and deleted, ``False`` otherwise.
        """
        doc = await self.get_user_document(document_id, user_id)
        if doc is None:
            return False
        await self.db.delete(doc)
        await self.db.commit()
        return True
