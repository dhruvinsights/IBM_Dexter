"""Pull request database model."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import ForeignKey, String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin


class PullRequest(TimestampMixin, Base):
    """Represent a repository pull request to be reviewed by Dexter."""

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    number: Mapped[int] = mapped_column(nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    repository_id: Mapped[int] = mapped_column(ForeignKey("repository.id"), nullable=False, index=True)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    state: Mapped[str] = mapped_column(String(50), default="open", nullable=False)

    repository: Mapped["Repository"] = relationship(back_populates="pull_requests")
    reviews: Mapped[list["Review"]] = relationship(
        back_populates="pull_request",
        cascade="all, delete-orphan",
    )
    memory_entries: Mapped[list["OrganizationMemory"]] = relationship(
        foreign_keys="OrganizationMemory.source_pr_id",
        back_populates="source_pr",
    )

# Made with Bob
