"""AI orchestration service for coordinating Dexter review agents."""

from __future__ import annotations

import logging
from typing import Any

from app.agents.architecture_agent import ArchitectureAgent
from app.agents.compliance_agent import ComplianceAgent
from app.agents.memory_agent import MemoryAgent
from app.agents.security_agent import SecurityAgent

logger = logging.getLogger(__name__)


class AIReviewService:
    """Coordinate multiple agents to generate a consolidated review."""

    def __init__(self) -> None:
        """Initialize all built-in review agents.
        
        ENHANCEMENT: Added MemoryAgent to leverage organizational learning,
        detect rejected patterns, and provide historical context from past reviews.
        """
        self.agents = [
            SecurityAgent(),
            ArchitectureAgent(),
            ComplianceAgent(),
            MemoryAgent(),  # Organizational learning and historical context
        ]

    async def review_code(
        self,
        pull_request: dict[str, Any],
        diffs: list[dict[str, Any]],
        context: list[str] | None = None,
    ) -> dict[str, Any]:
        """Run all configured agents and aggregate the results."""
        context = context or []
        agent_results: list[dict[str, Any]] = []

        for agent in self.agents:
            result = await agent.analyze(
                pull_request=pull_request,
                diffs=diffs,
                context=context,
            )
            agent_results.append(result)

        findings = [
            finding
            for result in agent_results
            for finding in result.get("findings", [])
        ]

        summary = {
            "status": "completed",
            "agent_count": len(agent_results),
            "findings_count": len(findings),
            "findings": findings,
            "agent_results": {result["agent"]: result for result in agent_results},
        }
        logger.info("AI review completed with %s findings", len(findings))
        return summary

# Made with Bob
