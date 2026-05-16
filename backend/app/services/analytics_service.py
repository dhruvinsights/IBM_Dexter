"""Analytics Service for Long-Term Engineering Intelligence."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.engineering_analytics import (
    ArchitectureIssuePattern,
    RepositoryRiskAssessment,
    TeamProductivityMetric,
    TechDebtMetric,
)

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Service for tracking and analyzing long-term engineering metrics.
    
    This service enables Dexter to provide insights into team productivity,
    technical debt trends, risk assessments, and recurring architecture issues.
    """

    async def record_team_productivity(
        self,
        db: AsyncSession,
        team_name: str,
        repository_id: int,
        period_start: datetime,
        period_end: datetime,
        metrics: Dict[str, Any],
    ) -> TeamProductivityMetric:
        """
        Record team productivity metrics for a period.
        
        Args:
            db: Database session
            team_name: Name of the team
            repository_id: Repository being measured
            period_start: Start of measurement period
            period_end: End of measurement period
            metrics: Dictionary of productivity metrics
            
        Returns:
            Created TeamProductivityMetric instance
        """
        metric = TeamProductivityMetric(
            team_name=team_name,
            repository_id=repository_id,
            period_start=period_start,
            period_end=period_end,
            total_prs=metrics.get("total_prs", 0),
            merged_prs=metrics.get("merged_prs", 0),
            rejected_prs=metrics.get("rejected_prs", 0),
            avg_review_time_hours=metrics.get("avg_review_time_hours", 0.0),
            avg_merge_time_hours=metrics.get("avg_merge_time_hours", 0.0),
            avg_review_iterations=metrics.get("avg_review_iterations", 0.0),
            avg_issues_per_pr=metrics.get("avg_issues_per_pr", 0.0),
            critical_issues_count=metrics.get("critical_issues_count", 0),
            security_issues_count=metrics.get("security_issues_count", 0),
            total_lines_added=metrics.get("total_lines_added", 0),
            total_lines_removed=metrics.get("total_lines_removed", 0),
            avg_pr_size=metrics.get("avg_pr_size", 0.0),
            policy_violations_count=metrics.get("policy_violations_count", 0),
            compliance_score=metrics.get("compliance_score", 100.0),
            metrics_data=metrics.get("additional_metrics", {}),
        )
        
        db.add(metric)
        await db.commit()
        await db.refresh(metric)
        
        logger.info(
            "Recorded productivity metrics for team %s (period: %s to %s)",
            team_name,
            period_start.date(),
            period_end.date(),
        )
        
        return metric

    async def get_team_productivity_trends(
        self,
        db: AsyncSession,
        team_name: Optional[str] = None,
        repository_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[TeamProductivityMetric]:
        """
        Get team productivity trends over time.
        
        Args:
            db: Database session
            team_name: Filter by team
            repository_id: Filter by repository
            start_date: Start of period
            end_date: End of period
            limit: Maximum number of results
            
        Returns:
            List of TeamProductivityMetric instances
        """
        query = select(TeamProductivityMetric)
        
        conditions = []
        if team_name:
            conditions.append(TeamProductivityMetric.team_name == team_name)
        if repository_id:
            conditions.append(TeamProductivityMetric.repository_id == repository_id)
        if start_date:
            conditions.append(TeamProductivityMetric.period_start >= start_date)
        if end_date:
            conditions.append(TeamProductivityMetric.period_end <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(desc(TeamProductivityMetric.period_start)).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())

    async def record_tech_debt(
        self,
        db: AsyncSession,
        repository_id: int,
        measurement_date: datetime,
        debt_scores: Dict[str, float],
        debt_items: List[Dict[str, Any]],
        legacy_ibm_components: Optional[List[str]] = None,
        modernization_opportunities: Optional[Dict[str, Any]] = None,
    ) -> TechDebtMetric:
        """
        Record technical debt measurement.
        
        Args:
            db: Database session
            repository_id: Repository being measured
            measurement_date: When measurement was taken
            debt_scores: Dictionary of debt scores by category
            debt_items: List of specific debt items
            legacy_ibm_components: Legacy IBM components identified
            modernization_opportunities: Modernization opportunities
            
        Returns:
            Created TechDebtMetric instance
        """
        total_debt_score = sum(debt_scores.values()) / len(debt_scores) if debt_scores else 0.0
        
        # Determine trend by comparing with previous measurement
        trend = "stable"
        prev_query = select(TechDebtMetric).where(
            and_(
                TechDebtMetric.repository_id == repository_id,
                TechDebtMetric.measurement_date < measurement_date,
            )
        ).order_by(desc(TechDebtMetric.measurement_date)).limit(1)
        
        prev_result = await db.execute(prev_query)
        prev_metric = prev_result.scalar_one_or_none()
        
        if prev_metric:
            if total_debt_score < prev_metric.total_debt_score - 5:
                trend = "improving"
            elif total_debt_score > prev_metric.total_debt_score + 5:
                trend = "worsening"
        
        critical_items = [item for item in debt_items if item.get("severity") == "critical"]
        
        metric = TechDebtMetric(
            repository_id=repository_id,
            measurement_date=measurement_date,
            architecture_debt_score=debt_scores.get("architecture", 0.0),
            code_quality_debt_score=debt_scores.get("code_quality", 0.0),
            security_debt_score=debt_scores.get("security", 0.0),
            documentation_debt_score=debt_scores.get("documentation", 0.0),
            test_coverage_debt_score=debt_scores.get("test_coverage", 0.0),
            total_debt_score=total_debt_score,
            debt_trend=trend,
            total_debt_issues=len(debt_items),
            critical_debt_issues=len(critical_items),
            legacy_ibm_components=legacy_ibm_components or [],
            modernization_opportunities=modernization_opportunities or {},
            debt_items=debt_items,
            estimated_effort_hours=sum(item.get("effort_hours", 0) for item in debt_items),
            priority_debt_effort_hours=sum(
                item.get("effort_hours", 0)
                for item in debt_items
                if item.get("priority") in ["critical", "high"]
            ),
        )
        
        db.add(metric)
        await db.commit()
        await db.refresh(metric)
        
        logger.info(
            "Recorded tech debt for repository %s: score=%.2f, trend=%s",
            repository_id,
            total_debt_score,
            trend,
        )
        
        return metric

    async def get_tech_debt_trends(
        self,
        db: AsyncSession,
        repository_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[TechDebtMetric]:
        """
        Get technical debt trends for a repository.
        
        Args:
            db: Database session
            repository_id: Repository to analyze
            start_date: Start of period
            end_date: End of period
            
        Returns:
            List of TechDebtMetric instances
        """
        query = select(TechDebtMetric).where(
            TechDebtMetric.repository_id == repository_id
        )
        
        if start_date:
            query = query.where(TechDebtMetric.measurement_date >= start_date)
        if end_date:
            query = query.where(TechDebtMetric.measurement_date <= end_date)
        
        query = query.order_by(TechDebtMetric.measurement_date)
        
        result = await db.execute(query)
        return list(result.scalars().all())

    async def assess_repository_risk(
        self,
        db: AsyncSession,
        repository_id: int,
        assessment_date: datetime,
        risk_scores: Dict[str, float],
        risk_factors: List[Dict[str, Any]],
        critical_vulnerabilities: int = 0,
        ibm_product_risks: Optional[Dict[str, Any]] = None,
        recommendations: Optional[List[Dict[str, Any]]] = None,
    ) -> RepositoryRiskAssessment:
        """
        Assess and record repository risk.
        
        Args:
            db: Database session
            repository_id: Repository being assessed
            assessment_date: When assessment was performed
            risk_scores: Dictionary of risk scores by category
            risk_factors: List of identified risk factors
            critical_vulnerabilities: Number of critical vulnerabilities
            ibm_product_risks: IBM product-specific risks
            recommendations: Risk mitigation recommendations
            
        Returns:
            Created RepositoryRiskAssessment instance
        """
        overall_risk_score = sum(risk_scores.values()) / len(risk_scores) if risk_scores else 0.0
        
        # Determine risk level
        if overall_risk_score >= 75:
            risk_level = "critical"
        elif overall_risk_score >= 50:
            risk_level = "high"
        elif overall_risk_score >= 25:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Get previous assessment for trend
        prev_query = select(RepositoryRiskAssessment).where(
            and_(
                RepositoryRiskAssessment.repository_id == repository_id,
                RepositoryRiskAssessment.assessment_date < assessment_date,
            )
        ).order_by(desc(RepositoryRiskAssessment.assessment_date)).limit(1)
        
        prev_result = await db.execute(prev_query)
        prev_assessment = prev_result.scalar_one_or_none()
        
        risk_trend = "stable"
        previous_risk_score = None
        
        if prev_assessment:
            previous_risk_score = prev_assessment.overall_risk_score
            if overall_risk_score < previous_risk_score - 10:
                risk_trend = "improving"
            elif overall_risk_score > previous_risk_score + 10:
                risk_trend = "worsening"
        
        # Extract priority actions from recommendations
        priority_actions = [
            rec.get("action", "")
            for rec in (recommendations or [])
            if rec.get("priority") in ["critical", "high"]
        ]
        
        assessment = RepositoryRiskAssessment(
            repository_id=repository_id,
            assessment_date=assessment_date,
            overall_risk_score=overall_risk_score,
            risk_level=risk_level,
            security_risk_score=risk_scores.get("security", 0.0),
            compliance_risk_score=risk_scores.get("compliance", 0.0),
            architecture_risk_score=risk_scores.get("architecture", 0.0),
            operational_risk_score=risk_scores.get("operational", 0.0),
            risk_factors=risk_factors,
            critical_vulnerabilities=critical_vulnerabilities,
            ibm_product_risks=ibm_product_risks or {},
            legacy_technology_risks=[
                factor.get("technology", "")
                for factor in risk_factors
                if factor.get("type") == "legacy_technology"
            ],
            recommendations=recommendations or [],
            priority_actions=priority_actions,
            risk_trend=risk_trend,
            previous_risk_score=previous_risk_score,
        )
        
        db.add(assessment)
        await db.commit()
        await db.refresh(assessment)
        
        logger.info(
            "Assessed repository %s risk: level=%s, score=%.2f",
            repository_id,
            risk_level,
            overall_risk_score,
        )
        
        return assessment

    async def get_risk_assessments(
        self,
        db: AsyncSession,
        repository_id: Optional[int] = None,
        risk_level: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[RepositoryRiskAssessment]:
        """
        Get repository risk assessments.
        
        Args:
            db: Database session
            repository_id: Filter by repository
            risk_level: Filter by risk level
            start_date: Start of period
            end_date: End of period
            
        Returns:
            List of RepositoryRiskAssessment instances
        """
        query = select(RepositoryRiskAssessment)
        
        conditions = []
        if repository_id:
            conditions.append(RepositoryRiskAssessment.repository_id == repository_id)
        if risk_level:
            conditions.append(RepositoryRiskAssessment.risk_level == risk_level)
        if start_date:
            conditions.append(RepositoryRiskAssessment.assessment_date >= start_date)
        if end_date:
            conditions.append(RepositoryRiskAssessment.assessment_date <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(desc(RepositoryRiskAssessment.assessment_date))
        
        result = await db.execute(query)
        return list(result.scalars().all())

    async def track_architecture_issue(
        self,
        db: AsyncSession,
        pattern_name: str,
        pattern_type: str,
        description: str,
        severity: str,
        impact_areas: List[str],
        resolution_approach: str,
        repository_id: int,
        team_name: str,
        related_ibm_products: Optional[List[str]] = None,
    ) -> ArchitectureIssuePattern:
        """
        Track a recurring architecture issue pattern.
        
        Args:
            db: Database session
            pattern_name: Unique pattern name
            pattern_type: Type of pattern
            description: Pattern description
            severity: Severity level
            impact_areas: Areas impacted
            resolution_approach: How to resolve
            repository_id: Repository where detected
            team_name: Team affected
            related_ibm_products: Related IBM products
            
        Returns:
            Created or updated ArchitectureIssuePattern instance
        """
        # Check if pattern exists
        query = select(ArchitectureIssuePattern).where(
            ArchitectureIssuePattern.pattern_name == pattern_name
        )
        result = await db.execute(query)
        pattern = result.scalar_one_or_none()
        
        if pattern:
            # Update existing pattern
            pattern.total_occurrences += 1
            if repository_id not in pattern.affected_repositories:
                pattern.affected_repositories.append(repository_id)
            if team_name not in pattern.affected_teams:
                pattern.affected_teams.append(team_name)
            
            logger.info(
                "Updated architecture pattern %s, now %d occurrences",
                pattern_name,
                pattern.total_occurrences,
            )
        else:
            # Create new pattern
            pattern = ArchitectureIssuePattern(
                pattern_name=pattern_name,
                pattern_type=pattern_type,
                description=description,
                total_occurrences=1,
                affected_repositories=[repository_id],
                affected_teams=[team_name],
                severity=severity,
                impact_areas=impact_areas,
                related_ibm_products=related_ibm_products or [],
                resolution_approach=resolution_approach,
            )
            db.add(pattern)
            
            logger.info("Created new architecture pattern: %s", pattern_name)
        
        await db.commit()
        await db.refresh(pattern)
        
        return pattern

    async def get_architecture_patterns(
        self,
        db: AsyncSession,
        pattern_type: Optional[str] = None,
        severity: Optional[str] = None,
        min_occurrences: int = 1,
        is_active: bool = True,
    ) -> List[ArchitectureIssuePattern]:
        """
        Get architecture issue patterns.
        
        Args:
            db: Database session
            pattern_type: Filter by pattern type
            severity: Filter by severity
            min_occurrences: Minimum occurrence count
            is_active: Filter by active status
            
        Returns:
            List of ArchitectureIssuePattern instances
        """
        query = select(ArchitectureIssuePattern)
        
        conditions = []
        if pattern_type:
            conditions.append(ArchitectureIssuePattern.pattern_type == pattern_type)
        if severity:
            conditions.append(ArchitectureIssuePattern.severity == severity)
        if min_occurrences > 1:
            conditions.append(ArchitectureIssuePattern.total_occurrences >= min_occurrences)
        if is_active is not None:
            conditions.append(ArchitectureIssuePattern.is_active == is_active)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(desc(ArchitectureIssuePattern.total_occurrences))
        
        result = await db.execute(query)
        return list(result.scalars().all())

    async def generate_analytics_summary(
        self,
        db: AsyncSession,
        repository_id: int,
        days: int = 30,
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive analytics summary for a repository.
        
        Args:
            db: Database session
            repository_id: Repository to analyze
            days: Number of days to include in analysis
            
        Returns:
            Analytics summary dictionary
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get productivity metrics
        productivity_metrics = await self.get_team_productivity_trends(
            db=db,
            repository_id=repository_id,
            start_date=start_date,
            end_date=end_date,
        )
        
        # Get tech debt trends
        debt_metrics = await self.get_tech_debt_trends(
            db=db,
            repository_id=repository_id,
            start_date=start_date,
            end_date=end_date,
        )
        
        # Get risk assessments
        risk_assessments = await self.get_risk_assessments(
            db=db,
            repository_id=repository_id,
            start_date=start_date,
            end_date=end_date,
        )
        
        # Calculate summary statistics
        summary = {
            "repository_id": repository_id,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days,
            },
            "productivity": {
                "total_prs": sum(m.total_prs for m in productivity_metrics),
                "merged_prs": sum(m.merged_prs for m in productivity_metrics),
                "avg_review_time_hours": (
                    sum(m.avg_review_time_hours for m in productivity_metrics) / len(productivity_metrics)
                    if productivity_metrics else 0.0
                ),
                "avg_compliance_score": (
                    sum(m.compliance_score for m in productivity_metrics) / len(productivity_metrics)
                    if productivity_metrics else 100.0
                ),
            },
            "tech_debt": {
                "current_score": debt_metrics[-1].total_debt_score if debt_metrics else 0.0,
                "trend": debt_metrics[-1].debt_trend if debt_metrics else "unknown",
                "critical_issues": debt_metrics[-1].critical_debt_issues if debt_metrics else 0,
            },
            "risk": {
                "current_level": risk_assessments[0].risk_level if risk_assessments else "unknown",
                "current_score": risk_assessments[0].overall_risk_score if risk_assessments else 0.0,
                "trend": risk_assessments[0].risk_trend if risk_assessments else "unknown",
            },
        }
        
        return summary

# Made with Bob