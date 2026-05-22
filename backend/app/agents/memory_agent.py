"""Memory Agent for Organization Learning and Historical Context."""

from __future__ import annotations

import logging
from typing import Any

from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class MemoryAgent(BaseAgent):
    """
    Specialized agent for leveraging organizational memory.
    
    This agent uses historical PR decisions, rejected patterns, and
    organizational conventions to provide context-aware reviews based
    on past learnings.
    """

    agent_name = "memory-agent"
    category = "organizational-learning"

    def __init__(self) -> None:
        """Initialize the memory agent."""
        super().__init__()
        # In production, this would connect to MemoryService
        self.pattern_cache: dict[str, Any] = {}

    async def analyze(
        self,
        pull_request: dict[str, Any],
        diffs: list[dict[str, Any]],
        context: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Analyze PR using organizational memory and historical context.
        
        Args:
            pull_request: PR metadata
            diffs: Code changes
            context: Historical context from MemoryService
            
        Returns:
            Structured findings based on organizational learning
        """
        findings: list[dict[str, Any]] = []
        
        # Check against rejected patterns
        rejected_findings = await self._check_rejected_patterns(diffs, context or [])
        findings.extend(rejected_findings)
        
        # Check against approved patterns
        approved_findings = await self._check_approved_patterns(diffs, context or [])
        findings.extend(approved_findings)
        
        # Check against architecture exceptions
        exception_findings = await self._check_architecture_exceptions(diffs, context or [])
        findings.extend(exception_findings)
        
        # Provide historical context
        context_findings = await self._provide_historical_context(pull_request, diffs, context or [])
        findings.extend(context_findings)
        
        summary = self._generate_summary(findings)
        
        return self.format_result(
            summary=summary,
            findings=findings,
            metadata={
                "total_insights": len(findings),
                "rejected_patterns_found": len(rejected_findings),
                "similar_past_decisions": len(context_findings),
            },
        )

    async def _check_rejected_patterns(
        self,
        diffs: list[dict[str, Any]],
        context: list[str],
    ) -> list[dict[str, Any]]:
        """Check for previously rejected patterns."""
        findings = []
        
        # Simulated rejected patterns (in production, from MemoryService)
        rejected_patterns = {
            "singleton_pattern": {
                "pattern": "class.*Singleton",
                "reason": "Team decided against singleton pattern for testability",
                "decision_date": "2024-03-15",
                "team": "Platform Team",
            },
            "global_state": {
                "pattern": "global\\s+\\w+\\s*=",
                "reason": "Global state causes issues in distributed systems",
                "decision_date": "2024-02-20",
                "team": "Architecture Team",
            },
            "synchronous_http": {
                "pattern": "requests\\.get|requests\\.post",
                "reason": "Prefer async HTTP clients for better performance",
                "decision_date": "2024-04-01",
                "team": "Backend Team",
            },
        }
        
        for diff in diffs:
            file_path = diff.get("filename") or diff.get("path", "")
            # ENHANCEMENT: Use full_content if available, otherwise fall back to patch
            content = diff.get("full_content") or diff.get("patch") or diff.get("content", "")
            
            for pattern_name, pattern_info in rejected_patterns.items():
                # Simplified pattern matching (in production, use regex)
                if any(keyword in content.lower() for keyword in pattern_info["pattern"].lower().split()):
                    findings.append({
                        "type": "rejected_pattern",
                        "severity": "high",
                        "file": file_path,
                        "pattern_name": pattern_name,
                        "message": f"Previously rejected pattern detected: {pattern_name}",
                        "description": pattern_info["reason"],
                        "historical_context": {
                            "decision_date": pattern_info["decision_date"],
                            "team": pattern_info["team"],
                        },
                        "remediation": f"This pattern was rejected by {pattern_info['team']} on {pattern_info['decision_date']}. {pattern_info['reason']}",
                    })
        
        return findings

    async def _check_approved_patterns(
        self,
        diffs: list[dict[str, Any]],
        context: list[str],
    ) -> list[dict[str, Any]]:
        """Check for approved organizational patterns."""
        findings = []
        
        # Simulated approved patterns
        approved_patterns = {
            "repository_pattern": {
                "indicators": ["repository", "interface"],
                "benefit": "Approved data access pattern for testability",
            },
            "dependency_injection": {
                "indicators": ["__init__", "inject"],
                "benefit": "Approved pattern for loose coupling",
            },
            "circuit_breaker": {
                "indicators": ["circuit", "breaker", "fallback"],
                "benefit": "Approved resilience pattern",
            },
        }
        
        for diff in diffs:
            file_path = diff.get("filename") or diff.get("path", "")
            # ENHANCEMENT: Use full_content if available for better pattern detection
            content = diff.get("full_content") or diff.get("patch") or diff.get("content", "")
            
            for pattern_name, pattern_info in approved_patterns.items():
                if all(indicator in content.lower() for indicator in pattern_info["indicators"]):
                    findings.append({
                        "type": "approved_pattern",
                        "severity": "info",
                        "file": file_path,
                        "pattern_name": pattern_name,
                        "message": f"Using approved pattern: {pattern_name}",
                        "description": pattern_info["benefit"],
                        "praise": "Good use of organizational best practice",
                    })
        
        return findings

    async def _check_architecture_exceptions(
        self,
        diffs: list[dict[str, Any]],
        context: list[str],
    ) -> list[dict[str, Any]]:
        """Check against documented architecture exceptions."""
        findings = []
        
        # Simulated architecture exceptions
        exceptions = {
            "legacy_api_v1": {
                "component": "api/v1",
                "exception": "Allowed to use synchronous calls for backward compatibility",
                "expiry": "2025-12-31",
                "approved_by": "Architecture Board",
            },
            "monolith_database": {
                "component": "core/database",
                "exception": "Allowed to use shared database until migration complete",
                "expiry": "2025-06-30",
                "approved_by": "CTO",
            },
        }
        
        for diff in diffs:
            file_path = diff.get("filename") or diff.get("path", "")
            
            for exception_name, exception_info in exceptions.items():
                if exception_info["component"] in file_path:
                    findings.append({
                        "type": "architecture_exception",
                        "severity": "info",
                        "file": file_path,
                        "exception_name": exception_name,
                        "message": f"Architecture exception applies: {exception_name}",
                        "description": exception_info["exception"],
                        "context": {
                            "approved_by": exception_info["approved_by"],
                            "expiry": exception_info["expiry"],
                        },
                        "note": f"This exception expires on {exception_info['expiry']}",
                    })
        
        return findings

    async def _provide_historical_context(
        self,
        pull_request: dict[str, Any],
        diffs: list[dict[str, Any]],
        context: list[str],
    ) -> list[dict[str, Any]]:
        """Provide historical context from similar past PRs."""
        findings = []
        
        # Simulated historical context (in production, from MemoryService)
        similar_prs = [
            {
                "pr_number": 1234,
                "title": "Similar refactoring in auth module",
                "decision": "Approved with additional tests",
                "lessons_learned": "Ensure backward compatibility with existing clients",
                "date": "2024-03-10",
            },
            {
                "pr_number": 1156,
                "title": "Database schema change",
                "decision": "Required migration script and rollback plan",
                "lessons_learned": "Always provide rollback strategy for schema changes",
                "date": "2024-02-15",
            },
        ]
        
        # Check if current PR is similar to past PRs
        pr_title = pull_request.get("title", "").lower()
        
        for past_pr in similar_prs:
            # Simplified similarity check
            if any(word in pr_title for word in past_pr["title"].lower().split()):
                findings.append({
                    "type": "historical_context",
                    "severity": "info",
                    "message": f"Similar to past PR #{past_pr['pr_number']}",
                    "description": f"Past PR: {past_pr['title']}",
                    "historical_decision": past_pr["decision"],
                    "lessons_learned": past_pr["lessons_learned"],
                    "reference": {
                        "pr_number": past_pr["pr_number"],
                        "date": past_pr["date"],
                    },
                    "recommendation": f"Consider: {past_pr['lessons_learned']}",
                })
        
        # Check for repeated issues in same files
        for diff in diffs:
            file_path = diff.get("filename") or diff.get("path", "")
            
            # Simulated file history
            if "auth" in file_path.lower():
                findings.append({
                    "type": "file_history",
                    "severity": "info",
                    "file": file_path,
                    "message": "This file has history of security issues",
                    "description": "Past reviews found 3 security issues in this file",
                    "recommendation": "Pay extra attention to authentication and authorization logic",
                    "past_issues": [
                        "SQL injection vulnerability (PR #1100)",
                        "Missing input validation (PR #1150)",
                        "Weak password hashing (PR #1200)",
                    ],
                })
        
        return findings

    async def _check_team_conventions(
        self,
        diffs: list[dict[str, Any]],
        context: list[str],
    ) -> list[dict[str, Any]]:
        """Check against team-specific conventions."""
        findings = []
        
        # Simulated team conventions
        conventions = {
            "naming": {
                "rule": "Use snake_case for Python functions",
                "team": "Backend Team",
            },
            "testing": {
                "rule": "All new features require integration tests",
                "team": "QA Team",
            },
            "documentation": {
                "rule": "Public APIs must have docstrings with examples",
                "team": "Platform Team",
            },
        }
        
        for diff in diffs:
            file_path = diff.get("filename") or diff.get("path", "")
            # ENHANCEMENT: Use full_content for better convention checking
            content = diff.get("full_content") or diff.get("patch") or diff.get("content", "")
            
            # Check naming convention
            if file_path.endswith(".py"):
                if "def " in content:
                    # Simplified check for camelCase (violation of snake_case)
                    if any(char.isupper() for char in content.split("def ")[1].split("(")[0] if "def " in content):
                        findings.append({
                            "type": "team_convention",
                            "severity": "low",
                            "file": file_path,
                            "convention": "naming",
                            "message": "Function naming doesn't follow team convention",
                            "description": conventions["naming"]["rule"],
                            "team": conventions["naming"]["team"],
                        })
        
        return findings

    def _generate_summary(self, findings: list[dict[str, Any]]) -> str:
        """Generate a summary of memory-based findings."""
        if not findings:
            return "No organizational memory insights for this PR"
        
        rejected = len([f for f in findings if f.get("type") == "rejected_pattern"])
        approved = len([f for f in findings if f.get("type") == "approved_pattern"])
        historical = len([f for f in findings if f.get("type") == "historical_context"])
        
        summary_parts = [f"Found {len(findings)} organizational insight(s)"]
        
        if rejected > 0:
            summary_parts.append(f"{rejected} rejected pattern(s) detected")
        
        if approved > 0:
            summary_parts.append(f"{approved} approved pattern(s) used")
        
        if historical > 0:
            summary_parts.append(f"{historical} similar past decision(s) found")
        
        return ". ".join(summary_parts)

# Made with Bob