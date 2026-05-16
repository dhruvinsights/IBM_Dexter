"""Engineering Analytics database model for Long-Term Intelligence."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import DateTime, Float, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin


class TeamProductivityMetric(TimestampMixin, Base):
    """
    Track team productivity metrics over time.
    
    This model captures key productivity indicators for engineering teams,
    enabling trend analysis, performance insights, and identification of
    areas for improvement.
    """

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Team identification
    team_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Name of the engineering team",
    )
    repository_id: Mapped[int] = mapped_column(
        nullable=False,
        index=True,
        comment="Repository being measured",
    )
    
    # Time period
    period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Start of measurement period",
    )
    period_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="End of measurement period",
    )
    
    # PR metrics
    total_prs: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Total PRs created in period",
    )
    merged_prs: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="PRs successfully merged",
    )
    rejected_prs: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="PRs rejected or closed without merge",
    )
    
    # Review metrics
    avg_review_time_hours: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Average time from PR creation to first review",
    )
    avg_merge_time_hours: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Average time from PR creation to merge",
    )
    avg_review_iterations: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Average number of review iterations per PR",
    )
    
    # Quality metrics
    avg_issues_per_pr: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Average issues found per PR",
    )
    critical_issues_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Total critical issues found",
    )
    security_issues_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Total security issues found",
    )
    
    # Code metrics
    total_lines_added: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Total lines of code added",
    )
    total_lines_removed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Total lines of code removed",
    )
    avg_pr_size: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Average PR size in lines changed",
    )
    
    # Compliance and governance
    policy_violations_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Total policy violations detected",
    )
    compliance_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=100.0,
        comment="Compliance score (0-100)",
    )
    
    # Additional metrics
    metrics_data: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Additional custom metrics",
    )


class TechDebtMetric(TimestampMixin, Base):
    """
    Track technical debt trends over time.
    
    This model monitors the accumulation and resolution of technical debt,
    helping teams understand debt trends and prioritize modernization efforts.
    """

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Identification
    repository_id: Mapped[int] = mapped_column(
        nullable=False,
        index=True,
        comment="Repository being measured",
    )
    measurement_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="When this measurement was taken",
    )
    
    # Debt categories
    architecture_debt_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Architecture debt score (0-100, higher is worse)",
    )
    code_quality_debt_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Code quality debt score",
    )
    security_debt_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Security debt score",
    )
    documentation_debt_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Documentation debt score",
    )
    test_coverage_debt_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Test coverage debt score",
    )
    
    # Overall metrics
    total_debt_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Overall technical debt score",
    )
    debt_trend: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="stable",
        comment="Trend: improving, stable, worsening",
    )
    
    # Issue tracking
    total_debt_issues: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Total number of debt items identified",
    )
    critical_debt_issues: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Critical debt items requiring immediate attention",
    )
    
    # IBM ecosystem specific
    legacy_ibm_components: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Legacy IBM components needing modernization",
    )
    modernization_opportunities: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Identified modernization opportunities",
    )
    
    # Detailed breakdown
    debt_items: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Detailed list of debt items",
    )
    
    # Estimates
    estimated_effort_hours: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Estimated effort to resolve all debt",
    )
    priority_debt_effort_hours: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Estimated effort for priority debt items",
    )


class RepositoryRiskAssessment(TimestampMixin, Base):
    """
    Assess and track repository risk levels.
    
    This model evaluates repositories for various risk factors including
    security vulnerabilities, compliance issues, and architectural problems.
    """

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Identification
    repository_id: Mapped[int] = mapped_column(
        nullable=False,
        index=True,
        comment="Repository being assessed",
    )
    assessment_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="When this assessment was performed",
    )
    
    # Overall risk
    overall_risk_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Overall risk score (0-100, higher is riskier)",
    )
    risk_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="low",
        index=True,
        comment="Risk level: critical, high, medium, low",
    )
    
    # Risk categories
    security_risk_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Security risk score",
    )
    compliance_risk_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Compliance risk score",
    )
    architecture_risk_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Architecture risk score",
    )
    operational_risk_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Operational risk score",
    )
    
    # Risk factors
    risk_factors: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Identified risk factors with details",
    )
    critical_vulnerabilities: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of critical vulnerabilities",
    )
    
    # IBM ecosystem risks
    ibm_product_risks: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Risks specific to IBM products in use",
    )
    legacy_technology_risks: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Risks from legacy technologies",
    )
    
    # Recommendations
    recommendations: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Risk mitigation recommendations",
    )
    priority_actions: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Priority actions to reduce risk",
    )
    
    # Trend analysis
    risk_trend: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="stable",
        comment="Risk trend: improving, stable, worsening",
    )
    previous_risk_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Previous assessment's risk score for comparison",
    )


class ArchitectureIssuePattern(TimestampMixin, Base):
    """
    Track repeated architecture issues across repositories.
    
    This model identifies and tracks recurring architecture problems,
    helping teams understand systemic issues and improve standards.
    """

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Pattern identification
    pattern_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="Unique name for this architecture issue pattern",
    )
    pattern_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Type: anti_pattern, code_smell, design_flaw, etc.",
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Description of the architecture issue",
    )
    
    # Occurrence tracking
    total_occurrences: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Total times this pattern has been detected",
    )
    affected_repositories: Mapped[list[int]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Repository IDs where this pattern appears",
    )
    affected_teams: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Teams affected by this pattern",
    )
    
    # Impact assessment
    severity: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="medium",
        comment="Severity of this architecture issue",
    )
    impact_areas: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Areas impacted: performance, security, maintainability, etc.",
    )
    estimated_impact_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Estimated impact score (0-100)",
    )
    
    # IBM ecosystem context
    related_ibm_products: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="IBM products related to this pattern",
    )
    
    # Resolution guidance
    resolution_approach: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Recommended approach to resolve this pattern",
    )
    refactoring_effort: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="medium",
        comment="Effort required: low, medium, high, very_high",
    )
    
    # Examples and references
    examples: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Examples of this pattern in codebases",
    )
    documentation_links: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Links to relevant documentation",
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
        comment="Whether this pattern is still being tracked",
    )

# Made with Bob