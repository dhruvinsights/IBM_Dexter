"""Format AI review output as GitHub Flavored Markdown for PR review comments."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple


def resolve_logo_url(settings: Any) -> Optional[str]:
    """Return a public HTTPS URL for the Dexter logo, or None if not usable on GitHub."""
    explicit = (getattr(settings, "dexter_logo_public_url", None) or "").strip()
    if explicit.startswith("https://"):
        return explicit
    base = (getattr(settings, "dexter_public_app_url", None) or "").strip().rstrip("/")
    if not base or "localhost" in base.lower() or "127.0.0.1" in base:
        return None
    if base.startswith("http://"):
        return None
    if base.startswith("https://"):
        return f"{base}/Dexter_logo.png"
    return None


def build_dexter_review_body(result: Dict[str, Any], logo_url: Optional[str]) -> str:
    """Build the main PR review comment body (GFM)."""
    lines: List[str] = []
    if logo_url:
        lines.append(
            f'<p align="left"><img src="{logo_url}" alt="IBM Dexter" width="96" height="96" /></p>\n'
        )
    lines.append("## IBM Dexter — AI code review\n")
    lines.append(
        "_Automated feedback from Security, Architecture, and Compliance agents. "
        "Verify suggestions in your own environment before merging._\n"
    )

    findings = result.get("findings") or []
    fc = result.get("findings_count", len(findings))
    lines.append(f"**Findings:** {fc}\n")

    agent_results = result.get("agent_results") or {}
    if isinstance(agent_results, dict):
        for agent_key, agent in agent_results.items():
            if not isinstance(agent, dict):
                continue
            name = agent.get("agent") or agent_key
            summary = (agent.get("summary") or "").strip()
            lines.append(f"### {name}\n")
            if summary:
                lines.append(f"{summary}\n")
            af = agent.get("findings") or []
            if not af:
                lines.append("_No findings._\n")
                continue
            for f in af[:25]:
                if not isinstance(f, dict):
                    continue
                sev = str(f.get("severity", "low")).upper()
                msg = f.get("message") or ""
                path = f.get("file") or f.get("path") or ""
                rec = f.get("recommendation")
                hint = f.get("line_hint")
                prefix = f"- **[{sev}]**"
                if path:
                    prefix += f" `{path}`"
                prefix += f" — {msg}"
                lines.append(prefix)
                if rec:
                    lines.append(f"  - *Suggestion:* {rec}")
                if hint:
                    lines.append(f"  - `{hint}`")
            if len(af) > 25:
                lines.append(f"\n_…and {len(af) - 25} more (see Dexter UI for full output)._")
            lines.append("")

    body = "\n".join(lines).strip()
    if len(body) > 65000:
        body = body[:64000] + "\n\n…_(truncated for GitHub size limit)_"
    return body


_SEVERITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3, "none": 4}


def collect_ranked_findings_for_inline(
    result: Dict[str, Any], max_items: int
) -> List[Tuple[str, Dict[str, Any]]]:
    """Flatten agent findings and sort by severity for inline PR comments."""
    items: List[Tuple[str, Dict[str, Any], int]] = []
    agent_results = result.get("agent_results") or {}
    if not isinstance(agent_results, dict):
        return []
    for agent_key, agent in agent_results.items():
        if not isinstance(agent, dict):
            continue
        label = str(agent.get("agent") or agent_key)
        for f in agent.get("findings") or []:
            if not isinstance(f, dict):
                continue
            sev = str(f.get("severity") or "low").lower()
            rank = _SEVERITY_RANK.get(sev, 5)
            items.append((label, f, rank))
    items.sort(key=lambda t: t[2])
    return [(label, f) for label, f, _ in items[:max_items]]


def build_inline_comment_body(agent_label: str, finding: Dict[str, Any]) -> str:
    """GitHub PR review comment with optional ```suggestion block."""
    sev = str(finding.get("severity", "low")).upper()
    msg = (finding.get("message") or "").strip()
    rec = (finding.get("recommendation") or "").strip()
    suggestion = (finding.get("suggestion") or finding.get("suggested_fix") or "").strip()
    parts: List[str] = [f"**Dexter ({agent_label})** — [{sev}]", "", msg]
    if rec:
        parts.extend(["", f"**Recommendation:** {rec}"])
    if suggestion:
        # Keep suggestion reasonably small for the review API
        if len(suggestion) > 6000:
            suggestion = suggestion[:5900] + "\n…"
        lines = suggestion.splitlines()
        if len(lines) > 1:
            parts.extend(["", "```suggestion"])
            parts.extend(lines)
            parts.append("```")
        else:
            parts.extend(["", "```suggestion", suggestion, "```"])
    return "\n".join(parts).strip()
