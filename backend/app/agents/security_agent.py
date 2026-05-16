"""Security-focused review agent powered by an LLM + secret regex pre-filter."""

from __future__ import annotations

import json
import logging
import re
from typing import Any, List

from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


# Compile once. These are the well-known "definitely sensitive" patterns we
# always want to flag without waiting on the LLM. The LLM is used to add
# higher-level reasoning on top.
_SECRET_PATTERNS: list[tuple[str, str, str]] = [
    ("aws_access_key", r"AKIA[0-9A-Z]{16}", "AWS Access Key ID"),
    ("aws_secret_key", r"(?i)aws(.{0,20})?(secret|sec)?(.{0,20})?[=:]\s*['\"][A-Za-z0-9/+=]{40}['\"]", "Possible AWS secret access key"),
    ("github_pat", r"ghp_[A-Za-z0-9]{30,}", "GitHub personal access token"),
    ("github_oauth", r"gho_[A-Za-z0-9]{30,}", "GitHub OAuth token"),
    ("slack_token", r"xox[abpr]-[A-Za-z0-9-]+", "Slack token"),
    ("generic_api_key", r"(?i)(api[_-]?key|secret|token|password)\s*[=:]\s*['\"][A-Za-z0-9_\-\.]{16,}['\"]", "Possible hardcoded credential"),
    ("private_key", r"-----BEGIN (RSA|DSA|EC|OPENSSH|PGP) PRIVATE KEY-----", "Embedded private key material"),
    ("jwt", r"eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}", "JWT token"),
]


_SYSTEM_PROMPT = """You are IBM Dexter's Security Agent, a senior application
security engineer reviewing a pull request. Identify concrete security issues
introduced by the diff. Focus on:
- Injection (SQL / shell / template) and unsafe deserialization
- Hardcoded secrets, weak crypto, insecure random
- AuthN/AuthZ bypass, missing authorization checks
- Sensitive data exposure (PII, secrets in logs)
- Insecure dependencies / unsafe network calls
- CORS / CSRF / SSRF risks

Return STRICT JSON only. No markdown, no commentary.
Schema:
{
  "summary": "<one paragraph executive summary>",
  "overall_severity": "critical|high|medium|low|none",
  "findings": [
    {
      "severity": "critical|high|medium|low",
      "file": "<path>",
      "line_hint": "<optional snippet, max ~80 chars>",
      "category": "<short tag, e.g. 'hardcoded-secret', 'sql-injection'>",
      "message": "<one sentence describing the issue>",
      "recommendation": "<one sentence describing the fix>",
      "confidence": 0.0
    }
  ]
}
If no findings, return findings: []."""


def _build_user_prompt(
    pull_request: dict[str, Any],
    diffs: list[dict[str, Any]],
    context: list[str],
) -> str:
    """Render the diff + RAG context into the user message."""
    pr_title = pull_request.get("title") or pull_request.get("name") or "(untitled)"
    pr_desc = pull_request.get("description") or pull_request.get("body") or ""

    lines: List[str] = [
        "## Pull Request",
        f"- title: {pr_title}",
        f"- number: {pull_request.get('number', 'n/a')}",
        f"- author: {pull_request.get('author') or pull_request.get('user', {}).get('login', 'unknown')}",
    ]
    if pr_desc:
        lines.append(f"- description: {pr_desc[:600]}")

    if context:
        lines.append("\n## Org Knowledge Base Context")
        for snippet in context[:6]:
            lines.append(f"- {snippet[:500]}")

    lines.append("\n## Changed Files")
    diff_budget = 14000  # rough char budget to keep prompt small for llama3
    used = 0
    for diff in diffs:
        filename = str(diff.get("filename") or diff.get("path") or "unknown")
        patch = str(diff.get("patch") or diff.get("content") or "")
        if not patch:
            continue
        if used + len(patch) > diff_budget:
            patch = patch[: max(diff_budget - used, 0)]
        if not patch:
            break
        used += len(patch)
        lines.append(f"\n### {filename}\n```diff\n{patch}\n```")
        if used >= diff_budget:
            break

    lines.append(
        "\nReturn STRICT JSON only matching the schema described in the system prompt."
    )
    return "\n".join(lines)


def _parse_llm_json(response: str) -> dict[str, Any] | None:
    """Extract the first JSON object from a (sometimes chatty) LLM response."""
    response = response.strip()
    if not response:
        return None
    if response.startswith("```"):
        response = response.strip("`")
        if response.lower().startswith("json"):
            response = response[4:]
        response = response.strip()
    # Find the largest balanced {...} substring.
    first = response.find("{")
    last = response.rfind("}")
    if first == -1 or last == -1 or last <= first:
        return None
    blob = response[first : last + 1]
    try:
        return json.loads(blob)
    except json.JSONDecodeError as exc:
        logger.warning("Security agent JSON parse failed: %s", exc)
        return None


class SecurityAgent(BaseAgent):
    """Detect security issues using fast regex pre-filters + LLM reasoning."""

    agent_name = "security-agent"
    category = "security"

    async def analyze(
        self,
        pull_request: dict[str, Any],
        diffs: list[dict[str, Any]],
        context: list[str] | None = None,
    ) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []
        context = context or []

        # Stage 1: deterministic regex sweep for well-known secret formats.
        for diff in diffs:
            filename = str(diff.get("filename") or diff.get("path") or "unknown")
            patch = str(diff.get("patch") or diff.get("content") or "")
            if not patch:
                continue
            for category, pattern, label in _SECRET_PATTERNS:
                if re.search(pattern, patch):
                    findings.append({
                        "severity": "critical",
                        "file": filename,
                        "category": f"hardcoded-secret/{category}",
                        "message": f"{label} detected in diff",
                        "recommendation": "Move the value to a secret manager / env var and rotate the leaked credential.",
                        "confidence": 0.95,
                        "source": "regex",
                    })

        # Stage 2: LLM review.
        llm_summary = "LLM analysis unavailable."
        overall = "low" if findings else "none"
        try:
            prompt = _SYSTEM_PROMPT + "\n\n" + _build_user_prompt(pull_request, diffs, context)
            response = await self.generate_llm_response(prompt=prompt, temperature=0.1, max_tokens=1200)
            parsed = _parse_llm_json(response)
            if parsed:
                llm_summary = str(parsed.get("summary") or llm_summary)
                overall = str(parsed.get("overall_severity") or overall)
                for raw in parsed.get("findings") or []:
                    if not isinstance(raw, dict):
                        continue
                    findings.append({
                        "severity": str(raw.get("severity", "medium")).lower(),
                        "file": raw.get("file") or "unknown",
                        "category": raw.get("category") or "security",
                        "message": raw.get("message") or "Security concern reported by LLM.",
                        "recommendation": raw.get("recommendation") or "Review the highlighted code.",
                        "line_hint": raw.get("line_hint"),
                        "confidence": float(raw.get("confidence") or 0.7),
                        "source": "llm",
                    })
            else:
                # If parsing failed, surface the raw text as a low-confidence finding.
                findings.append({
                    "severity": "low",
                    "file": "(general)",
                    "category": "security-llm-note",
                    "message": response.strip()[:400] if response else "LLM produced no output.",
                    "recommendation": "Re-run analysis or inspect manually.",
                    "confidence": 0.3,
                    "source": "llm-raw",
                })
        except Exception as exc:
            logger.warning("Security LLM call failed: %s", exc)

        summary = (
            f"Security review for PR {pull_request.get('number', 'unknown')}: "
            f"{len(findings)} finding(s). {llm_summary}"
        )
        return self.format_result(
            summary=summary,
            findings=findings,
            metadata={
                "context_used": bool(context),
                "rag_chunks": len(context),
                "overall_severity": overall,
                "regex_findings": sum(1 for f in findings if f.get("source") == "regex"),
                "llm_findings": sum(1 for f in findings if f.get("source") == "llm"),
            },
        )


# Made with Bob
