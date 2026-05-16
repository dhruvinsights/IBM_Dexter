"""Organization Memory database model for Enterprise Intelligence Layer."""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import ForeignKey, JSON, String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin


class OrganizationMemory(TimestampMixin, Base):
    """
    Represent historical PR decisions and organizational learning.
    
    This model stores the institutional knowledge that Dexter builds over time,
    including past PR decisions, architecture exceptions, rejected patterns,
    and internal conventions. This enables Dexter to provide context-aware
    reviews based on the organization's history and preferences.
    """

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Core identification
    decision_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Type: architecture_exception, rejected_pattern, approved_pattern, convention, etc.",
    )
    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Brief title describing the decision or pattern",
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Detailed description of the decision, pattern, or convention",
    )
    
    # Context and rationale
    rationale: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Why this decision was made or pattern was rejected/approved",
    )
    context: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Additional context: affected systems, technologies, constraints",
    )
    
    # Source information
    source_pr_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("pullrequest.id"),
        nullable=True,
        index=True,
        comment="Original PR that led to this decision (if applicable)",
    )
    source_repository_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("repository.id"),
        nullable=True,
        index=True,
        comment="Repository where this decision originated",
    )
    
    # Team and ownership
    team_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Team that made or owns this decision",
    )
    decision_maker: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Person or role who made the final decision",
    )
    
    # Categorization and search
    tags: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Tags for categorization and search",
    )
    affected_components: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Components, services, or modules affected by this decision",
    )
    
    # IBM Ecosystem specific
    ibm_products: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="IBM products/services related to this decision",
    )
    
    # Status and lifecycle
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
        comment="Whether this decision is still active/relevant",
    )
    superseded_by_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("organizationmemory.id"),
        nullable=True,
        comment="ID of the decision that supersedes this one",
    )
    
    # Relationships
    source_pr: Mapped["PullRequest"] = relationship(
        foreign_keys=[source_pr_id],
        back_populates="memory_entries",
    )
    source_repository: Mapped["Repository"] = relationship(
        foreign_keys=[source_repository_id],
        back_populates="memory_entries",
    )
    superseded_by: Mapped["OrganizationMemory"] = relationship(
        foreign_keys=[superseded_by_id],
        remote_side=[id],
    )


class HistoricalPattern(TimestampMixin, Base):
    """
    Track recurring patterns detected across PRs for analytics.
    
    This model helps identify repeated issues, common mistakes, and
    emerging trends in the codebase over time.
    """

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    pattern_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Type: security_issue, architecture_violation, code_smell, etc.",
    )
    pattern_signature: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True,
        comment="Unique signature for pattern matching",
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Description of the pattern",
    )
    
    # Occurrence tracking
    occurrence_count: Mapped[int] = mapped_column(
        default=1,
        nullable=False,
        comment="Number of times this pattern has been detected",
    )
    first_seen_pr_id: Mapped[int] = mapped_column(
        ForeignKey("pullrequest.id"),
        nullable=False,
        index=True,
        comment="First PR where this pattern was detected",
    )
    last_seen_pr_id: Mapped[int] = mapped_column(
        ForeignKey("pullrequest.id"),
        nullable=False,
        index=True,
        comment="Most recent PR where this pattern was detected",
    )
    
    # Impact and severity
    severity: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="medium",
        comment="Severity: critical, high, medium, low, info",
    )
    impact_areas: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Areas impacted: security, performance, maintainability, etc.",
    )
    
    # Repository and team context
    repository_ids: Mapped[list[int]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Repositories where this pattern has been seen",
    )
    affected_teams: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Teams that have encountered this pattern",
    )
    
    # Resolution tracking
    resolution_guidance: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Recommended approach to resolve this pattern",
    )
    is_resolved: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        comment="Whether this pattern has been systematically addressed",
    )

# Made with Bob