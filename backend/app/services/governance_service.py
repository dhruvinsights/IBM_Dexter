"""Governance Service for Enterprise Compliance Layer."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.governance_policy import GovernancePolicy, PolicyViolation

logger = logging.getLogger(__name__)


class GovernanceService:
    """
    Service for managing governance policies and compliance enforcement.
    
    This service enables Dexter to enforce enterprise policies, track
    compliance violations, and generate audit trails for regulatory
    requirements.
    """

    async def create_policy(
        self,
        db: AsyncSession,
        name: str,
        display_name: str,
        description: str,
        policy_type: str,
        category: str,
        rules: Dict[str, Any],
        enforcement_level: str = "warning",
        severity: str = "medium",
        remediation_guidance: str = "",
        ibm_products: Optional[List[str]] = None,
        applies_to_file_patterns: Optional[List[str]] = None,
        applies_to_languages: Optional[List[str]] = None,
        compliance_frameworks: Optional[List[str]] = None,
        is_custom: bool = False,
    ) -> GovernancePolicy:
        """
        Create a new governance policy.
        
        Args:
            db: Database session
            name: Unique policy name
            display_name: Human-readable name
            description: Policy description
            policy_type: Type (security, architecture, compliance, etc.)
            category: Category (ibm_ecosystem, cloud_native, etc.)
            rules: Policy rules in structured format
            enforcement_level: blocking, error, warning, info
            severity: critical, high, medium, low
            remediation_guidance: How to fix violations
            ibm_products: IBM products this applies to
            applies_to_file_patterns: File patterns to check
            applies_to_languages: Programming languages
            compliance_frameworks: Compliance frameworks supported
            is_custom: Whether this is a custom policy
            
        Returns:
            Created GovernancePolicy instance
        """
        policy = GovernancePolicy(
            name=name,
            display_name=display_name,
            description=description,
            policy_type=policy_type,
            category=category,
            rules=rules,
            enforcement_level=enforcement_level,
            severity=severity,
            remediation_guidance=remediation_guidance,
            ibm_products=ibm_products or [],
            applies_to_file_patterns=applies_to_file_patterns or [],
            applies_to_languages=applies_to_languages or [],
            compliance_frameworks=compliance_frameworks or [],
            is_custom=is_custom,
        )
        
        db.add(policy)
        await db.commit()
        await db.refresh(policy)
        
        logger.info(
            "Created governance policy: %s (type: %s, enforcement: %s)",
            name,
            policy_type,
            enforcement_level,
        )
        
        return policy

    async def get_policies(
        self,
        db: AsyncSession,
        policy_type: Optional[str] = None,
        category: Optional[str] = None,
        enforcement_level: Optional[str] = None,
        is_active: bool = True,
        ibm_product: Optional[str] = None,
    ) -> List[GovernancePolicy]:
        """
        Query governance policies with filters.
        
        Args:
            db: Database session
            policy_type: Filter by policy type
            category: Filter by category
            enforcement_level: Filter by enforcement level
            is_active: Filter by active status
            ibm_product: Filter by IBM product
            
        Returns:
            List of matching GovernancePolicy instances
        """
        query = select(GovernancePolicy)
        
        conditions = []
        if policy_type:
            conditions.append(GovernancePolicy.policy_type == policy_type)
        if category:
            conditions.append(GovernancePolicy.category == category)
        if enforcement_level:
            conditions.append(GovernancePolicy.enforcement_level == enforcement_level)
        if is_active is not None:
            conditions.append(GovernancePolicy.is_active == is_active)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(GovernancePolicy.name)
        
        result = await db.execute(query)
        policies = list(result.scalars().all())
        
        # Post-filter for IBM product (JSON array)
        if ibm_product:
            policies = [p for p in policies if ibm_product in p.ibm_products]
        
        return policies

    async def get_policy_by_name(
        self,
        db: AsyncSession,
        name: str,
    ) -> GovernancePolicy | None:
        """
        Get a policy by its unique name.
        
        Args:
            db: Database session
            name: Policy name
            
        Returns:
            GovernancePolicy instance or None
        """
        query = select(GovernancePolicy).where(GovernancePolicy.name == name)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def update_policy(
        self,
        db: AsyncSession,
        policy_id: int,
        **updates: Any,
    ) -> GovernancePolicy:
        """
        Update a governance policy.
        
        Args:
            db: Database session
            policy_id: Policy ID to update
            **updates: Fields to update
            
        Returns:
            Updated GovernancePolicy instance
        """
        query = select(GovernancePolicy).where(GovernancePolicy.id == policy_id)
        result = await db.execute(query)
        policy = result.scalar_one()
        
        for key, value in updates.items():
            if hasattr(policy, key):
                setattr(policy, key, value)
        
        await db.commit()
        await db.refresh(policy)
        
        logger.info("Updated policy %s", policy.name)
        
        return policy

    async def record_violation(
        self,
        db: AsyncSession,
        policy_id: int,
        policy_name: str,
        review_id: int,
        pull_request_id: int,
        repository_id: int,
        file_path: str,
        violation_message: str,
        severity: str,
        enforcement_level: str,
        line_number: Optional[int] = None,
        violation_context: Optional[Dict[str, Any]] = None,
    ) -> PolicyViolation:
        """
        Record a policy violation.
        
        Args:
            db: Database session
            policy_id: ID of violated policy
            policy_name: Name of violated policy
            review_id: Review where violation was detected
            pull_request_id: PR where violation occurred
            repository_id: Repository where violation occurred
            file_path: File with violation
            violation_message: Violation message
            severity: Severity level
            enforcement_level: Enforcement level
            line_number: Line number of violation
            violation_context: Additional context
            
        Returns:
            Created PolicyViolation instance
        """
        violation = PolicyViolation(
            policy_id=policy_id,
            policy_name=policy_name,
            review_id=review_id,
            pull_request_id=pull_request_id,
            repository_id=repository_id,
            file_path=file_path,
            violation_message=violation_message,
            severity=severity,
            enforcement_level=enforcement_level,
            line_number=line_number,
            violation_context=violation_context or {},
        )
        
        db.add(violation)
        await db.commit()
        await db.refresh(violation)
        
        logger.info(
            "Recorded policy violation: %s in %s (severity: %s)",
            policy_name,
            file_path,
            severity,
        )
        
        return violation

    async def get_violations(
        self,
        db: AsyncSession,
        repository_id: Optional[int] = None,
        pull_request_id: Optional[int] = None,
        policy_name: Optional[str] = None,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 100,
    ) -> List[PolicyViolation]:
        """
        Query policy violations with filters.
        
        Args:
            db: Database session
            repository_id: Filter by repository
            pull_request_id: Filter by PR
            policy_name: Filter by policy name
            status: Filter by status
            severity: Filter by severity
            limit: Maximum number of results
            
        Returns:
            List of matching PolicyViolation instances
        """
        query = select(PolicyViolation)
        
        conditions = []
        if repository_id:
            conditions.append(PolicyViolation.repository_id == repository_id)
        if pull_request_id:
            conditions.append(PolicyViolation.pull_request_id == pull_request_id)
        if policy_name:
            conditions.append(PolicyViolation.policy_name == policy_name)
        if status:
            conditions.append(PolicyViolation.status == status)
        if severity:
            conditions.append(PolicyViolation.severity == severity)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(desc(PolicyViolation.created_at)).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())

    async def resolve_violation(
        self,
        db: AsyncSession,
        violation_id: int,
        resolution_notes: str,
    ) -> PolicyViolation:
        """
        Mark a violation as resolved.
        
        Args:
            db: Database session
            violation_id: Violation ID
            resolution_notes: Notes about resolution
            
        Returns:
            Updated PolicyViolation instance
        """
        query = select(PolicyViolation).where(PolicyViolation.id == violation_id)
        result = await db.execute(query)
        violation = result.scalar_one()
        
        violation.status = "resolved"
        violation.resolution_notes = resolution_notes
        
        await db.commit()
        await db.refresh(violation)
        
        logger.info("Resolved violation %s", violation_id)
        
        return violation

    async def waive_violation(
        self,
        db: AsyncSession,
        violation_id: int,
        waived_by: str,
        waiver_reason: str,
    ) -> PolicyViolation:
        """
        Waive a policy violation.
        
        Args:
            db: Database session
            violation_id: Violation ID
            waived_by: Who waived the violation
            waiver_reason: Reason for waiving
            
        Returns:
            Updated PolicyViolation instance
        """
        query = select(PolicyViolation).where(PolicyViolation.id == violation_id)
        result = await db.execute(query)
        violation = result.scalar_one()
        
        violation.status = "waived"
        violation.waived_by = waived_by
        violation.waiver_reason = waiver_reason
        
        await db.commit()
        await db.refresh(violation)
        
        logger.info("Waived violation %s by %s", violation_id, waived_by)
        
        return violation

    async def get_compliance_report(
        self,
        db: AsyncSession,
        repository_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Generate a compliance report for a repository.
        
        Args:
            db: Database session
            repository_id: Repository to report on
            start_date: Start of reporting period
            end_date: End of reporting period
            
        Returns:
            Compliance report dictionary
        """
        query = select(PolicyViolation).where(
            PolicyViolation.repository_id == repository_id
        )
        
        if start_date:
            query = query.where(PolicyViolation.created_at >= start_date)
        if end_date:
            query = query.where(PolicyViolation.created_at <= end_date)
        
        result = await db.execute(query)
        violations = list(result.scalars().all())
        
        # Calculate statistics
        total_violations = len(violations)
        by_severity = {}
        by_status = {}
        by_policy = {}
        
        for violation in violations:
            # Count by severity
            by_severity[violation.severity] = by_severity.get(violation.severity, 0) + 1
            
            # Count by status
            by_status[violation.status] = by_status.get(violation.status, 0) + 1
            
            # Count by policy
            by_policy[violation.policy_name] = by_policy.get(violation.policy_name, 0) + 1
        
        open_violations = by_status.get("open", 0)
        resolved_violations = by_status.get("resolved", 0)
        
        compliance_score = 100.0
        if total_violations > 0:
            compliance_score = (resolved_violations / total_violations) * 100
        
        report = {
            "repository_id": repository_id,
            "period": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None,
            },
            "summary": {
                "total_violations": total_violations,
                "open_violations": open_violations,
                "resolved_violations": resolved_violations,
                "compliance_score": round(compliance_score, 2),
            },
            "by_severity": by_severity,
            "by_status": by_status,
            "by_policy": by_policy,
            "top_violations": [
                {
                    "policy_name": policy,
                    "count": count,
                }
                for policy, count in sorted(
                    by_policy.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )[:10]
            ],
        }
        
        return report

    async def get_audit_trail(
        self,
        db: AsyncSession,
        repository_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """
        Get audit trail of policy violations and resolutions.
        
        Args:
            db: Database session
            repository_id: Filter by repository
            start_date: Start of audit period
            end_date: End of audit period
            limit: Maximum number of entries
            
        Returns:
            List of audit trail entries
        """
        query = select(PolicyViolation)
        
        conditions = []
        if repository_id:
            conditions.append(PolicyViolation.repository_id == repository_id)
        if start_date:
            conditions.append(PolicyViolation.created_at >= start_date)
        if end_date:
            conditions.append(PolicyViolation.created_at <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(desc(PolicyViolation.created_at)).limit(limit)
        
        result = await db.execute(query)
        violations = result.scalars().all()
        
        audit_trail = []
        for violation in violations:
            entry = {
                "timestamp": violation.created_at.isoformat(),
                "event_type": "policy_violation",
                "policy_name": violation.policy_name,
                "severity": violation.severity,
                "enforcement_level": violation.enforcement_level,
                "repository_id": violation.repository_id,
                "pull_request_id": violation.pull_request_id,
                "file_path": violation.file_path,
                "status": violation.status,
            }
            
            if violation.status == "waived":
                entry["waived_by"] = violation.waived_by
                entry["waiver_reason"] = violation.waiver_reason
            elif violation.status == "resolved":
                entry["resolution_notes"] = violation.resolution_notes
            
            audit_trail.append(entry)
        
        return audit_trail

# Made with Bob