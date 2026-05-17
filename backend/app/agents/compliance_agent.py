"""Compliance-focused review agent."""

from __future__ import annotations

from typing import Any

from app.agents.base_agent import BaseAgent
from app.services.diff_comment_map import first_added_line_number


class ComplianceAgent(BaseAgent):
    """Analyze pull request diffs for compliance and governance signals."""

    agent_name = "compliance-agent"
    category = "compliance"

    async def analyze(
        self,
        pull_request: dict[str, Any],
        diffs: list[dict[str, Any]],
        context: list[str] | None = None,
    ) -> dict[str, Any]:
        """Inspect diffs for logging, auditability, and policy gaps."""
        findings: list[dict[str, Any]] = []

        for diff in diffs:
            patch = str(diff.get("patch", ""))
            filename = str(diff.get("filename", "unknown"))
            if "delete" in patch.lower() and "audit" not in patch.lower():
                ln = first_added_line_number(patch)
                findings.append(
                    {
                        "severity": "medium",
                        "file": filename,
                        "line": ln,
                        "message": "Destructive logic detected without obvious audit trail handling.",
                    }
                )

        summary = (
            f"Compliance review completed for PR {pull_request.get('number', 'unknown')} "
            f"with {len(findings)} finding(s)."
        )
        return self.format_result(summary=summary, findings=findings, metadata={"context_used": bool(context)})

# Made with Bob
