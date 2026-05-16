"""Repository database model."""

from __future__ import annotations

from typing import Any

from sqlalchemy import Boolean, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin


class Repository(TimestampMixin, Base):
    """Represent a source code repository connected to IBM Dexter."""

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String(50), nullable=False, default="github")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    settings: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    owner: Mapped["User"] = relationship(back_populates="repositories")
    pull_requests: Mapped[list["PullRequest"]] = relationship(
        back_populates="repository",
        cascade="all, delete-orphan",
    )
    memory_entries: Mapped[list["OrganizationMemory"]] = relationship(
        foreign_keys="OrganizationMemory.source_repository_id",
        back_populates="source_repository",
    )

# Made with Bob
