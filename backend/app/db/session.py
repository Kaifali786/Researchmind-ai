"""
Async session factory and FastAPI dependency for database sessions.

Provides:
- ``async_session_factory``: Bound to the async engine, produces sessions.
- ``get_db``: An async generator used as a FastAPI ``Depends(get_db)``
  dependency that yields a session and guarantees cleanup.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.base import async_engine

async_session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides a scoped async database session.

    Yields:
        An ``AsyncSession`` instance. The session is automatically closed
        when the request finishes, regardless of success or failure.

    Usage::

        @router.get("/items")
        async def list_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
