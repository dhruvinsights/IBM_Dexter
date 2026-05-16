"""Governance Policy database model for Enterprise Compliance Layer."""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import Boolean, JSON, String, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin


class GovernancePolicy(TimestampMixin, Base):
    """
    Represent enterprise governance policies and compliance rules.
    
    This model defines the policies that Dexter enforces during code reviews,
    including security requirements, architecture standards, compliance rules,
    and IBM ecosystem best practices. Policies can be configured per organization,
    team, or repository.
    """

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Policy identification
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="Unique policy name",
    )
    display_name: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Human-readable policy name",
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Detailed description of what this policy enforces",
    )
    
    # Policy categorization
    policy_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Type: security, architecture, compliance, performance, maintainability",
    )
    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Category: ibm_ecosystem, cloud_native, enterprise_standards, regulatory",
    )
    
    # Enforcement configuration
    enforcement_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="warning",
        comment="Level: blocking, error, warning, info",
    )
    severity: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="medium",
        comment="Severity: critical, high, medium, low",
    )
    
    # IBM Ecosystem specifics
    ibm_products: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="IBM products this policy applies to: OpenShift, WebSphere, Db2, MQ, etc.",
    )
    ibm_versions: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Version constraints for IBM products",
    )
    
    # Policy rules and conditions
    rules: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        comment="Policy rules in structured format for evaluation",
    )
    conditions: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Conditions under which this policy applies",
    )
    
    # Scope and applicability
    applies_to_file_patterns: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="File patterns this policy applies to (glob patterns)",
    )
    excludes_file_patterns: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="File patterns to exclude from this policy",
    )
    applies_to_languages: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Programming languages this policy applies to",
    )
    
    # Remediation guidance
    remediation_guidance: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="How to fix violations of this policy",
    )
    documentation_url: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
        comment="Link to detailed documentation",
    )
    examples: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Good and bad examples for this policy",
    )
    
    # Compliance and audit
    compliance_frameworks: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Compliance frameworks this policy supports: SOC2, HIPAA, PCI-DSS, etc.",
    )
    audit_required: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether violations require audit trail",
    )
    
    # Status and lifecycle
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether this policy is currently enforced",
    )
    is_custom: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether this is a custom organization policy",
    )
    
    # Metadata
    tags: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Tags for categorization and filtering",
    )
    owner_team: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Team responsible for maintaining this policy",
    )


class PolicyViolation(TimestampMixin, Base):
    """
    Track policy violations detected during code reviews.
    
    This model records all policy violations found by Dexter, enabling
    audit trails, compliance reporting, and trend analysis.
    """

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Violation identification
    policy_id: Mapped[int] = mapped_column(
        nullable=False,
        index=True,
        comment="ID of the violated policy (not FK to allow policy deletion)",
    )
    policy_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Name of violated policy (denormalized for audit)",
    )
    
    # Context
    review_id: Mapped[int] = mapped_column(
        nullable=False,
        index=True,
        comment="Review where violation was detected (not FK for flexibility)",
    )
    pull_request_id: Mapped[int] = mapped_column(
        nullable=False,
        index=True,
        comment="PR where violation occurred",
    )
    repository_id: Mapped[int] = mapped_column(
        nullable=False,
        index=True,
        comment="Repository where violation occurred",
    )
    
    # Violation details
    file_path: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
        comment="File where violation was found",
    )
    line_number: Mapped[Optional[int]] = mapped_column(
        nullable=True,
        comment="Line number of violation",
    )
    violation_message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Detailed violation message",
    )
    violation_context: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Additional context about the violation",
    )
    
    # Severity and impact
    severity: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Severity at time of detection",
    )
    enforcement_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Enforcement level at time of detection",
    )
    
    # Resolution tracking
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="open",
        index=True,
        comment="Status: open, resolved, waived, false_positive",
    )
    resolution_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Notes about how violation was resolved",
    )
    waived_by: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Who waived this violation (if applicable)",
    )
    waiver_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Reason for waiving this violation",
    )

# Made with Bob