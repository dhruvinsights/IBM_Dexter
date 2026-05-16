"""Security-focused review agent."""

from __future__ import annotations

from typing import Any

from app.agents.base_agent import BaseAgent


class SecurityAgent(BaseAgent):
    """Analyze pull request diffs for common security concerns."""

    agent_name = "security-agent"
    category = "security"

    async def analyze(
        self,
        pull_request: dict[str, Any],
        diffs: list[dict[str, Any]],
        context: list[str] | None = None,
    ) -> dict[str, Any]:
        """Inspect diffs for dangerous patterns and missing controls."""
        findings: list[dict[str, Any]] = []

        for diff in diffs:
            patch = str(diff.get("patch", ""))
            filename = str(diff.get("filename", "unknown"))
            if "password" in patch.lower() or "secret" in patch.lower():
                findings.append(
                    {
                        "severity": "high",
                        "file": filename,
                        "message": "Potential hardcoded credential detected.",
                    }
                )

        summary = (
            f"Security review completed for PR {pull_request.get('number', 'unknown')} "
            f"with {len(findings)} finding(s)."
        )
        return self.format_result(summary=summary, findings=findings, metadata={"context_used": bool(context)})

# Made with Bob
