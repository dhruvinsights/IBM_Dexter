"""Organization Memory Service for Enterprise Intelligence Layer."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization_memory import HistoricalPattern, OrganizationMemory
from app.models.pull_request import PullRequest

logger = logging.getLogger(__name__)


class MemoryService:
    """
    Service for managing organizational memory and historical decisions.
    
    This service enables Dexter to learn from past PR decisions, track
    rejected patterns, and provide context-aware reviews based on
    organizational history.
    """

    async def store_decision(
        self,
        db: AsyncSession,
        decision_type: str,
        title: str,
        description: str,
        rationale: str,
        team_name: str,
        decision_maker: str,
        context: Optional[Dict[str, Any]] = None,
        source_pr_id: Optional[int] = None,
        source_repository_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
        affected_components: Optional[List[str]] = None,
        ibm_products: Optional[List[str]] = None,
    ) -> OrganizationMemory:
        """
        Store a new organizational decision or pattern.
        
        Args:
            db: Database session
            decision_type: Type of decision (architecture_exception, rejected_pattern, etc.)
            title: Brief title of the decision
            description: Detailed description
            rationale: Why this decision was made
            team_name: Team that made the decision
            decision_maker: Person who made the final decision
            context: Additional context dictionary
            source_pr_id: PR that led to this decision
            source_repository_id: Repository where decision originated
            tags: Tags for categorization
            affected_components: Components affected by this decision
            ibm_products: IBM products related to this decision
            
        Returns:
            Created OrganizationMemory instance
        """
        memory = OrganizationMemory(
            decision_type=decision_type,
            title=title,
            description=description,
            rationale=rationale,
            team_name=team_name,
            decision_maker=decision_maker,
            context=context or {},
            source_pr_id=source_pr_id,
            source_repository_id=source_repository_id,
            tags=tags or [],
            affected_components=affected_components or [],
            ibm_products=ibm_products or [],
        )
        
        db.add(memory)
        await db.commit()
        await db.refresh(memory)
        
        logger.info(
            "Stored organizational decision: %s (type: %s, team: %s)",
            title,
            decision_type,
            team_name,
        )
        
        return memory

    async def get_decisions(
        self,
        db: AsyncSession,
        decision_type: Optional[str] = None,
        team_name: Optional[str] = None,
        tags: Optional[List[str]] = None,
        ibm_products: Optional[List[str]] = None,
        is_active: bool = True,
        limit: int = 100,
    ) -> List[OrganizationMemory]:
        """
        Query organizational decisions with filters.
        
        Args:
            db: Database session
            decision_type: Filter by decision type
            team_name: Filter by team
            tags: Filter by tags (any match)
            ibm_products: Filter by IBM products (any match)
            is_active: Filter by active status
            limit: Maximum number of results
            
        Returns:
            List of matching OrganizationMemory instances
        """
        query = select(OrganizationMemory)
        
        conditions = []
        if decision_type:
            conditions.append(OrganizationMemory.decision_type == decision_type)
        if team_name:
            conditions.append(OrganizationMemory.team_name == team_name)
        if is_active is not None:
            conditions.append(OrganizationMemory.is_active == is_active)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # JSON array filtering for tags and ibm_products would require database-specific syntax
        # For now, we'll filter in Python after fetching
        
        query = query.order_by(desc(OrganizationMemory.created_at)).limit(limit)
        
        result = await db.execute(query)
        memories = list(result.scalars().all())
        
        # Post-filter for tags and IBM products
        if tags:
            memories = [m for m in memories if any(tag in m.tags for tag in tags)]
        if ibm_products:
            memories = [m for m in memories if any(prod in m.ibm_products for prod in ibm_products)]
        
        return memories

    async def find_similar_decisions(
        self,
        db: AsyncSession,
        pr_id: int,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Find similar past decisions for a given PR.
        
        This uses simple heuristics based on repository, components, and tags.
        In production, this could use vector similarity or more advanced matching.
        
        Args:
            db: Database session
            pr_id: Pull request ID to find similar decisions for
            limit: Maximum number of results
            
        Returns:
            List of similar decisions with similarity scores
        """
        # Get the PR details
        pr_query = select(PullRequest).where(PullRequest.id == pr_id)
        pr_result = await db.execute(pr_query)
        pr = pr_result.scalar_one_or_none()
        
        if not pr:
            logger.warning("PR %s not found for similarity search", pr_id)
            return []
        
        # Find decisions from the same repository
        query = select(OrganizationMemory).where(
            and_(
                OrganizationMemory.source_repository_id == pr.repository_id,
                OrganizationMemory.is_active == True,
            )
        ).order_by(desc(OrganizationMemory.created_at)).limit(limit)
        
        result = await db.execute(query)
        similar_decisions = result.scalars().all()
        
        # Format results with similarity scores (simplified)
        results = []
        for decision in similar_decisions:
            results.append({
                "decision": {
                    "id": decision.id,
                    "title": decision.title,
                    "decision_type": decision.decision_type,
                    "description": decision.description,
                    "rationale": decision.rationale,
                    "team_name": decision.team_name,
                    "created_at": decision.created_at.isoformat(),
                },
                "similarity_score": 0.8,  # Placeholder - would be calculated in production
                "match_reasons": ["same_repository"],
            })
        
        return results

    async def track_pattern(
        self,
        db: AsyncSession,
        pattern_type: str,
        pattern_signature: str,
        description: str,
        pr_id: int,
        severity: str = "medium",
        impact_areas: Optional[List[str]] = None,
        resolution_guidance: Optional[str] = None,
    ) -> HistoricalPattern:
        """
        Track a recurring pattern detected in a PR.
        
        Args:
            db: Database session
            pattern_type: Type of pattern (security_issue, architecture_violation, etc.)
            pattern_signature: Unique signature for pattern matching
            description: Description of the pattern
            pr_id: PR where pattern was detected
            severity: Severity level
            impact_areas: Areas impacted by this pattern
            resolution_guidance: How to resolve this pattern
            
        Returns:
            Created or updated HistoricalPattern instance
        """
        # Check if pattern already exists
        query = select(HistoricalPattern).where(
            HistoricalPattern.pattern_signature == pattern_signature
        )
        result = await db.execute(query)
        pattern = result.scalar_one_or_none()
        
        if pattern:
            # Update existing pattern
            pattern.occurrence_count += 1
            pattern.last_seen_pr_id = pr_id
            logger.info(
                "Updated pattern %s, now seen %d times",
                pattern_signature,
                pattern.occurrence_count,
            )
        else:
            # Create new pattern
            pattern = HistoricalPattern(
                pattern_type=pattern_type,
                pattern_signature=pattern_signature,
                description=description,
                first_seen_pr_id=pr_id,
                last_seen_pr_id=pr_id,
                severity=severity,
                impact_areas=impact_areas or [],
                resolution_guidance=resolution_guidance,
            )
            db.add(pattern)
            logger.info("Created new pattern: %s", pattern_signature)
        
        await db.commit()
        await db.refresh(pattern)
        
        return pattern

    async def get_patterns(
        self,
        db: AsyncSession,
        pattern_type: Optional[str] = None,
        severity: Optional[str] = None,
        min_occurrences: int = 1,
        is_resolved: Optional[bool] = None,
        limit: int = 100,
    ) -> List[HistoricalPattern]:
        """
        Query historical patterns with filters.
        
        Args:
            db: Database session
            pattern_type: Filter by pattern type
            severity: Filter by severity
            min_occurrences: Minimum occurrence count
            is_resolved: Filter by resolution status
            limit: Maximum number of results
            
        Returns:
            List of matching HistoricalPattern instances
        """
        query = select(HistoricalPattern)
        
        conditions = []
        if pattern_type:
            conditions.append(HistoricalPattern.pattern_type == pattern_type)
        if severity:
            conditions.append(HistoricalPattern.severity == severity)
        if min_occurrences > 1:
            conditions.append(HistoricalPattern.occurrence_count >= min_occurrences)
        if is_resolved is not None:
            conditions.append(HistoricalPattern.is_resolved == is_resolved)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(desc(HistoricalPattern.occurrence_count)).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())

    async def supersede_decision(
        self,
        db: AsyncSession,
        old_decision_id: int,
        new_decision_id: int,
    ) -> OrganizationMemory:
        """
        Mark an old decision as superseded by a new one.
        
        Args:
            db: Database session
            old_decision_id: ID of decision being superseded
            new_decision_id: ID of new decision
            
        Returns:
            Updated old decision
        """
        query = select(OrganizationMemory).where(OrganizationMemory.id == old_decision_id)
        result = await db.execute(query)
        old_decision = result.scalar_one()
        
        old_decision.is_active = False
        old_decision.superseded_by_id = new_decision_id
        
        await db.commit()
        await db.refresh(old_decision)
        
        logger.info(
            "Decision %s superseded by %s",
            old_decision_id,
            new_decision_id,
        )
        
        return old_decision

    async def get_context_for_review(
        self,
        db: AsyncSession,
        repository_id: int,
        components: Optional[List[str]] = None,
        ibm_products: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Get relevant organizational context for a code review.
        
        Args:
            db: Database session
            repository_id: Repository being reviewed
            components: Components being modified
            ibm_products: IBM products in use
            
        Returns:
            Dictionary with relevant context
        """
        # Get recent decisions for this repository
        decisions_query = select(OrganizationMemory).where(
            and_(
                OrganizationMemory.source_repository_id == repository_id,
                OrganizationMemory.is_active == True,
            )
        ).order_by(desc(OrganizationMemory.created_at)).limit(10)
        
        decisions_result = await db.execute(decisions_query)
        decisions = list(decisions_result.scalars().all())
        
        # Get relevant patterns
        patterns_query = select(HistoricalPattern).where(
            HistoricalPattern.is_resolved == False
        ).order_by(desc(HistoricalPattern.occurrence_count)).limit(10)
        
        patterns_result = await db.execute(patterns_query)
        patterns = list(patterns_result.scalars().all())
        
        context = {
            "recent_decisions": [
                {
                    "id": d.id,
                    "title": d.title,
                    "decision_type": d.decision_type,
                    "rationale": d.rationale,
                    "team_name": d.team_name,
                }
                for d in decisions
            ],
            "active_patterns": [
                {
                    "pattern_type": p.pattern_type,
                    "description": p.description,
                    "occurrence_count": p.occurrence_count,
                    "severity": p.severity,
                }
                for p in patterns
            ],
        }
        
        return context

# Made with Bob