"""Map unified-diff patches to PR head line numbers for GitHub inline review comments."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

_HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def iter_added_lines_in_patch(patch: str) -> List[Tuple[int, str]]:
    """Return (new_file_line_number, line text without leading '+') for each added line."""
    if not patch or patch.startswith("Binary files"):
        return []
    out: List[Tuple[int, str]] = []
    in_hunk = False
    new_line = 0
    for raw in patch.splitlines():
        if raw.startswith("@@"):
            m = _HUNK_RE.match(raw)
            if m:
                new_line = int(m.group(3))
                in_hunk = True
            continue
        if not in_hunk:
            continue
        if not raw:
            continue
        prefix = raw[0]
        if prefix == "+":
            if raw.startswith("+++"):
                continue
            out.append((new_line, raw[1:]))
            new_line += 1
        elif prefix == " ":
            new_line += 1
        elif prefix == "-":
            continue
        elif prefix == "\\":
            continue
    return out


def first_added_line_number(patch: str) -> Optional[int]:
    rows = iter_added_lines_in_patch(patch)
    return rows[0][0] if rows else None


def added_line_numbers(filename: str, patch_by_file: Dict[str, str]) -> List[int]:
    patch = patch_by_file.get(filename) or patch_by_file.get(filename.replace("\\", "/"))
    if not patch:
        return []
    return [ln for ln, _ in iter_added_lines_in_patch(patch)]


def resolve_review_line(
    filename: str,
    finding: Dict[str, Any],
    patch_by_file: Dict[str, str],
) -> Optional[int]:
    """Pick a RIGHT-side line number for a finding, using structured line, hints, or patch."""
    patch = patch_by_file.get(filename) or patch_by_file.get(filename.replace("\\", "/"))
    if not patch:
        return None
    added = iter_added_lines_in_patch(patch)
    line_set = {ln for ln, _ in added}

    raw_line = finding.get("line")
    if isinstance(raw_line, float):
        raw_line = int(raw_line) if raw_line == int(raw_line) else None
    if isinstance(raw_line, int) and raw_line > 0 and raw_line in line_set:
        return raw_line
    # Coerce string digits from LLM
    if isinstance(raw_line, str) and raw_line.isdigit():
        n = int(raw_line)
        if n in line_set:
            return n

    hint = (finding.get("line_hint") or "").strip()
    if hint:
        for ln, content in added:
            if hint in content or content.strip() in hint:
                return ln
        short = hint[:60] if len(hint) > 60 else hint
        for ln, content in added:
            if short in content:
                return ln

    if added:
        return added[0][0]
    return None


def build_patch_index(diffs: List[Dict[str, Any]]) -> Dict[str, str]:
    """filename -> patch string."""
    out: Dict[str, str] = {}
    for d in diffs:
        fn = str(d.get("filename") or d.get("path") or "")
        p = d.get("patch") or ""
        if fn and isinstance(p, str):
            out[fn] = p
    return out
