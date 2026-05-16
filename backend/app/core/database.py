"""Database configuration and session management for IBM Dexter."""

from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, declared_attr, mapped_column
from sqlalchemy.pool import NullPool

from app.core.config import get_settings

settings = get_settings()

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


def _build_engine() -> AsyncEngine:
    """Create the SQLAlchemy async engine with environment-aware pooling."""
    is_sqlite = settings.database_url.startswith("sqlite")
    engine_kwargs: dict[str, Any] = {
        "echo": settings.database_echo,
        "future": True,
    }

    if is_sqlite:
        engine_kwargs["poolclass"] = NullPool
    else:
        engine_kwargs["pool_size"] = settings.database_pool_size
        engine_kwargs["max_overflow"] = settings.database_max_overflow
        engine_kwargs["pool_pre_ping"] = True

    return create_async_engine(settings.database_url, **engine_kwargs)


engine: AsyncEngine = _build_engine()
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """Declarative SQLAlchemy base with naming conventions and timestamp helpers."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Generate table names automatically from model names."""
        return cls.__name__.lower()


class TimestampMixin:
    """Provide created and updated timestamp columns."""

    created_at = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        default=datetime.utcnow,
    )
    updated_at = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        default=datetime.utcnow,
    )


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a managed asynchronous database session."""
    async with AsyncSessionLocal() as session:
        yield session

# Made with Bob
