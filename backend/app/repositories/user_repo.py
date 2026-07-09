"""
User repository — data-access layer for the ``users`` table.

Extends ``BaseRepository`` with user-specific look-up helpers.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Async repository for User CRUD and look-ups.

    Inherits generic ``create``, ``get_by_id``, ``update``, ``delete``
    from ``BaseRepository``.
    """

    model = User

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialise the user repository.

        Args:
            db: Active async database session.
        """
        super().__init__(db)

    async def get_by_email(self, email: str) -> User | None:
        """
        Look up a user by their email address (case-insensitive).

        Args:
            email: The email to search for.

        Returns:
            The ``User`` instance if found, otherwise ``None``.
        """
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalars().first()

    async def get_by_username(self, username: str) -> User | None:
        """
        Look up a user by username.

        Args:
            username: The username to search for.

        Returns:
            The ``User`` instance if found, otherwise ``None``.
        """
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalars().first()

    async def email_exists(self, email: str) -> bool:
        """
        Check whether an email address is already registered.

        Args:
            email: Email to check.

        Returns:
            ``True`` if a user with this email exists.
        """
        user = await self.get_by_email(email)
        return user is not None

    async def username_exists(self, username: str) -> bool:
        """
        Check whether a username is already taken.

        Args:
            username: Username to check.

        Returns:
            ``True`` if a user with this username exists.
        """
        user = await self.get_by_username(username)
        return user is not None

    async def get_active_users(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        """
        Fetch only active (non-deactivated) users.

        Args:
            skip: Pagination offset.
            limit: Page size.

        Returns:
            List of active ``User`` instances.
        """
        result = await self.db.execute(
            select(User)
            .where(User.is_active.is_(True))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
