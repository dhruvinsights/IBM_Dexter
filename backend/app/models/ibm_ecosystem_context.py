"""IBM Ecosystem Context database model for IBM Product Intelligence."""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import Boolean, JSON, String, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin


class IBMEcosystemContext(TimestampMixin, Base):
    """
    Store IBM product/service context and best practices.
    
    This model maintains knowledge about IBM ecosystem products, their
    configurations, best practices, known issues, and migration paths.
    This enables Dexter to provide IBM-specific intelligence during reviews.
    """

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Product identification
    product_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="IBM product/service name: OpenShift, WebSphere, Db2, MQ, etc.",
    )
    product_family: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Product family: middleware, database, cloud, ai, mainframe",
    )
    product_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Type: application_server, database, message_queue, container_platform, etc.",
    )
    
    # Version information
    version: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Product version",
    )
    version_family: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Major version family (e.g., '9.x', '11.x')",
    )
    is_latest_version: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether this is the latest version",
    )
    is_supported: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether this version is still supported by IBM",
    )
    end_of_support_date: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="End of support date (ISO format)",
    )
    
    # Configuration patterns
    recommended_configurations: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Recommended configuration patterns",
    )
    security_configurations: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Security-specific configurations",
    )
    performance_configurations: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Performance optimization configurations",
    )
    
    # Best practices
    best_practices: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Best practices for this product/version",
    )
    anti_patterns: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Known anti-patterns to avoid",
    )
    
    # Known issues
    known_issues: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Known issues and their workarounds",
    )
    security_vulnerabilities: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Known security vulnerabilities",
    )
    
    # Migration and modernization
    migration_paths: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Migration paths to newer versions or products",
    )
    modernization_recommendations: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Recommendations for modernizing to cloud-native",
    )
    compatibility_matrix: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Compatibility with other IBM products",
    )
    
    # Integration patterns
    integration_patterns: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Common integration patterns with other systems",
    )
    api_patterns: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="API usage patterns and examples",
    )
    
    # Cloud-native considerations
    cloud_native_patterns: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Cloud-native deployment patterns",
    )
    kubernetes_configurations: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Kubernetes/OpenShift specific configurations",
    )
    
    # Documentation and resources
    documentation_urls: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Links to official documentation",
    )
    tutorial_urls: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Links to tutorials and guides",
    )
    
    # Metadata
    tags: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Tags for categorization",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether this context is actively maintained",
    )


class IBMProductDetection(TimestampMixin, Base):
    """
    Track detected IBM products in repositories.
    
    This model records which IBM products are detected in each repository,
    enabling targeted reviews and recommendations.
    """

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Repository context
    repository_id: Mapped[int] = mapped_column(
        nullable=False,
        index=True,
        comment="Repository where product was detected",
    )
    
    # Product information
    product_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Detected IBM product name",
    )
    detected_version: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Detected version (if identifiable)",
    )
    
    # Detection details
    detection_method: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="How product was detected: config_file, dependency, code_pattern, etc.",
    )
    detection_confidence: Mapped[float] = mapped_column(
        nullable=False,
        default=1.0,
        comment="Confidence score (0-1)",
    )
    detection_evidence: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Evidence supporting the detection",
    )
    
    # File locations
    detected_in_files: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Files where product usage was detected",
    )
    configuration_files: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Configuration files for this product",
    )
    
    # Usage analysis
    usage_patterns: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Detected usage patterns",
    )
    integration_points: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Integration points with other systems",
    )
    
    # Assessment
    is_legacy: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether this is a legacy version",
    )
    needs_modernization: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether modernization is recommended",
    )
    modernization_priority: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="low",
        comment="Priority: critical, high, medium, low",
    )
    
    # Recommendations
    recommendations: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Recommendations for this product usage",
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether this product is still in active use",
    )
    last_verified_date: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Last date this detection was verified",
    )


class IBMBestPracticeViolation(TimestampMixin, Base):
    """
    Track violations of IBM product best practices.
    
    This model records when code violates IBM product best practices,
    enabling teams to improve their IBM ecosystem implementations.
    """

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Context
    repository_id: Mapped[int] = mapped_column(
        nullable=False,
        index=True,
        comment="Repository where violation occurred",
    )
    pull_request_id: Mapped[Optional[int]] = mapped_column(
        nullable=True,
        index=True,
        comment="PR where violation was detected (if applicable)",
    )
    review_id: Mapped[Optional[int]] = mapped_column(
        nullable=True,
        index=True,
        comment="Review where violation was detected",
    )
    
    # Product context
    product_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="IBM product related to this violation",
    )
    product_version: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Product version",
    )
    
    # Violation details
    violation_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Type: configuration, security, performance, integration, etc.",
    )
    best_practice_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="ID of the violated best practice",
    )
    best_practice_title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Title of the best practice",
    )
    violation_description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Description of the violation",
    )
    
    # Location
    file_path: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
        comment="File where violation was found",
    )
    line_number: Mapped[Optional[int]] = mapped_column(
        nullable=True,
        comment="Line number of violation",
    )
    code_snippet: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Code snippet showing the violation",
    )
    
    # Severity and impact
    severity: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="medium",
        comment="Severity: critical, high, medium, low",
    )
    impact_areas: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Impact areas: security, performance, reliability, etc.",
    )
    
    # Remediation
    remediation_guidance: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="How to fix this violation",
    )
    correct_example: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Example of correct implementation",
    )
    documentation_url: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
        comment="Link to relevant documentation",
    )
    
    # Status
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
        comment="Notes about resolution",
    )

# Made with Bob