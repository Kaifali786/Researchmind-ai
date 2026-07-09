"""
SQLAlchemy async engine and declarative base.

Creates:
- ``async_engine``: The global async engine bound to the configured DB URL.
- ``Base``: The ORM declarative base all models inherit from.
"""

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

settings = get_settings()

engine_kwargs = {
    "echo": settings.DATABASE_ECHO,
    "pool_pre_ping": True,
    "pool_recycle": 3600,
}

if "sqlite" not in settings.DATABASE_URL:
    engine_kwargs["pool_size"] = settings.DATABASE_POOL_SIZE
    engine_kwargs["max_overflow"] = settings.DATABASE_MAX_OVERFLOW

async_engine = create_async_engine(
    settings.DATABASE_URL,
    **engine_kwargs
)



class Base(DeclarativeBase):
    """
    Declarative base for all SQLAlchemy ORM models.

    Every model must inherit from this class so that Alembic auto-generation
    and ``metadata.create_all`` work correctly.
    """

    pass
