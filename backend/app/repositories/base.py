"""
Generic async base repository implementing common CRUD operations.

All domain-specific repositories inherit from ``BaseRepository`` to avoid
duplicating boilerplate SELECT / INSERT / UPDATE / DELETE logic.
"""

from typing import Any, Generic, Sequence, TypeVar
from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Async repository base providing CRUD primitives.

    Type Parameters:
        ModelType: The SQLAlchemy model class this repository manages.

    Attributes:
        model: The ORM model class (set by subclasses).
        db: The active async database session.
    """

    model: type[ModelType]

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialise with a database session.

        Args:
            db: An active ``AsyncSession`` (typically injected via FastAPI Depends).
        """
        self.db = db

    async def get_by_id(self, record_id: UUID) -> ModelType | None:
        """
        Fetch a single record by its primary key.

        Args:
            record_id: UUID primary key.

        Returns:
            The model instance if found, otherwise ``None``.
        """
        result = await self.db.execute(
            select(self.model).where(self.model.id == record_id)
        )
        return result.scalars().first()

    async def get_all(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[ModelType]:
        """
        Fetch multiple records with offset / limit pagination.

        Args:
            skip: Number of records to skip (offset).
            limit: Maximum number of records to return.

        Returns:
            A sequence of model instances.
        """
        result = await self.db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def count(self) -> int:
        """
        Return the total number of rows in the table.

        Returns:
            Integer row count.
        """
        result = await self.db.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar_one()

    async def create(self, obj_in: dict[str, Any]) -> ModelType:
        """
        Insert a new record.

        Args:
            obj_in: Dictionary of column values.

        Returns:
            The newly created and refreshed model instance.
        """
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        record_id: UUID,
        obj_in: dict[str, Any],
    ) -> ModelType | None:
        """
        Update an existing record by primary key.

        Args:
            record_id: UUID of the record to update.
            obj_in: Dictionary of column values to change. Keys with ``None``
                     values are skipped to support partial updates.

        Returns:
            The updated model instance, or ``None`` if the record was not found.
        """
        # Strip None values for partial update semantics
        update_data = {k: v for k, v in obj_in.items() if v is not None}
        if not update_data:
            return await self.get_by_id(record_id)

        await self.db.execute(
            update(self.model)
            .where(self.model.id == record_id)
            .values(**update_data)
        )
        await self.db.commit()
        return await self.get_by_id(record_id)

    async def delete(self, record_id: UUID) -> bool:
        """
        Delete a record by primary key.

        Args:
            record_id: UUID of the record to delete.

        Returns:
            ``True`` if a row was deleted, ``False`` if no matching row existed.
        """
        result = await self.db.execute(
            delete(self.model).where(self.model.id == record_id)
        )
        await self.db.commit()
        return result.rowcount > 0

    async def get_by_field(
        self,
        field_name: str,
        value: Any,
    ) -> ModelType | None:
        """
        Look up a single record by an arbitrary column.

        Args:
            field_name: Column name on the model.
            value: Value to match.

        Returns:
            The first matching model instance, or ``None``.

        Raises:
            AttributeError: If the model does not have the given column.
        """
        column = getattr(self.model, field_name)
        result = await self.db.execute(
            select(self.model).where(column == value)
        )
        return result.scalars().first()

    async def get_many_by_field(
        self,
        field_name: str,
        value: Any,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[ModelType]:
        """
        Fetch multiple records filtered by an arbitrary column.

        Args:
            field_name: Column name on the model.
            value: Value to match.
            skip: Offset for pagination.
            limit: Maximum results.

        Returns:
            Sequence of matching model instances.
        """
        column = getattr(self.model, field_name)
        result = await self.db.execute(
            select(self.model).where(column == value).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def count_by_field(self, field_name: str, value: Any) -> int:
        """
        Count records matching a column value.

        Args:
            field_name: Column name on the model.
            value: Value to match.

        Returns:
            Integer count.
        """
        column = getattr(self.model, field_name)
        result = await self.db.execute(
            select(func.count()).select_from(self.model).where(column == value)
        )
        return result.scalar_one()
