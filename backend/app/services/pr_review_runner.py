"""Shared GitHub PR analysis + optional GitHub review submission (summary + inline)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import get_settings
from app.services.ai_service import AIReviewService
from app.services.diff_comment_map import build_patch_index, resolve_review_line
from app.services.github_review_format import (
    build_dexter_review_body,
    build_inline_comment_body,
    collect_ranked_findings_for_inline,
    resolve_logo_url,
)
from app.services.github_service import GitHubService
from app.services.knowledge_base_service import get_knowledge_base_service

logger = logging.getLogger(__name__)
settings = get_settings()


async def run_github_pr_review(
    owner: str,
    repo: str,
    pull_number: int,
    *,
    head_sha: Optional[str] = None,
    use_rag: bool = True,
    rag_query: Optional[str] = None,
    rag_limit: int = 4,
    post_review_to_github: bool = False,
    request_self_as_reviewer: bool = False,
    inline_review_comments: bool = True,
    max_inline_comments: int = 35,
) -> Dict[str, Any]:
    """
    Fetch PR from GitHub, run agents, optionally post a PR review with inline comments.
    Returns the same structure the analyze-url endpoint persists (without HTTPException).
    """
    github = GitHubService()

    try:
        pr_meta = await github.fetch_pr_details(owner, repo, pull_number)
        files = await github.get_file_diffs(owner, repo, pull_number)
    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code if exc.response else 0
        detail = exc.response.text[:500] if exc.response is not None else str(exc)
        return {
            "ok": False,
            "error": "github_http_error",
            "status_code": status_code,
            "detail": detail,
        }
    except httpx.RequestError as exc:
        return {"ok": False, "error": "github_network", "detail": str(exc)}

    head_sha = head_sha or (pr_meta.get("head") or {}).get("sha")
    if not head_sha:
        return {"ok": False, "error": "missing_head_sha"}

    diffs: List[Dict[str, Any]] = [
        {
            "filename": f.get("filename"),
            "status": f.get("status"),
            "additions": f.get("additions"),
            "deletions": f.get("deletions"),
            "patch": f.get("patch") or "",
        }
        for f in files
    ]

    pull_request: Dict[str, Any] = {
        "id": pr_meta.get("id"),
        "number": pr_meta.get("number"),
        "title": pr_meta.get("title"),
        "description": (pr_meta.get("body") or "")[:2000],
        "author": (pr_meta.get("user") or {}).get("login"),
        "state": pr_meta.get("state"),
        "html_url": pr_meta.get("html_url"),
        "base": (pr_meta.get("base") or {}).get("ref"),
        "head": (pr_meta.get("head") or {}).get("ref"),
        "repository": f"{owner}/{repo}",
    }

    rag_context: List[str] = []
    rag_meta: Dict[str, Any] = {"enabled": use_rag, "retrieved": 0}
    if use_rag:
        try:
            kb = get_knowledge_base_service()
            query = rag_query or (pull_request.get("title") or "") + " " + (pull_request.get("description") or "")
            query = query.strip() or "code review best practices"
            rag_context = await kb.context_for(query, limit=rag_limit)
            rag_meta["retrieved"] = len(rag_context)
            rag_meta["backend"] = kb.get_backend_info()
        except Exception as exc:  # noqa: BLE001
            logger.warning("RAG retrieval skipped: %s", exc)
            rag_meta["error"] = str(exc)

    review_service = AIReviewService()
    result = await review_service.review_code(
        pull_request=pull_request,
        diffs=diffs,
        context=rag_context,
    )

    review_record: Dict[str, Any] = {
        "pull_request": pull_request,
        "rag": rag_meta,
        "stats": {
            "file_count": len(diffs),
            "additions": sum(d.get("additions") or 0 for d in diffs),
            "deletions": sum(d.get("deletions") or 0 for d in diffs),
        },
        "status": result["status"],
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "result": result,
        "ok": True,
    }

    gh_meta: Dict[str, Any] = {"posted_review": False, "inline_comments": 0}
    if post_review_to_github or request_self_as_reviewer:
        if not github.headers.get("Authorization"):
            gh_meta["error"] = "GitHub token required — set DEXTER_GITHUB_TOKEN or save a PAT in Settings."
        else:
            inline_payload: Optional[List[Dict[str, Any]]] = None
            if post_review_to_github and inline_review_comments:
                patch_by_file = build_patch_index(diffs)
                ranked = collect_ranked_findings_for_inline(result, max_inline_comments * 2)
                inline_payload = []
                seen_keys: set[tuple[str, int]] = set()
                for agent_label, finding in ranked:
                    path = str(finding.get("file") or finding.get("path") or "").strip()
                    if not path or path == "(general)":
                        continue
                    line = resolve_review_line(path, finding, patch_by_file)
                    if line is None:
                        continue
                    body = build_inline_comment_body(agent_label, finding)
                    key = (path, line)
                    if key in seen_keys:
                        continue
                    seen_keys.add(key)
                    inline_payload.append({
                        "path": path,
                        "body": body,
                        "line": line,
                        "side": "RIGHT",
                    })
                    if len(inline_payload) >= max_inline_comments:
                        break
                if not inline_payload:
                    inline_payload = None
                gh_meta["inline_comments"] = len(inline_payload or [])

            if post_review_to_github:
                try:
                    logo = resolve_logo_url(settings)
                    body_md = build_dexter_review_body(result, logo)
                    gh_review = await github.post_review_comments(
                        owner,
                        repo,
                        pull_number,
                        body_md,
                        commit_id=head_sha if inline_payload else None,
                        comments=inline_payload,
                    )
                    gh_meta["posted_review"] = True
                    gh_meta["review_id"] = gh_review.get("id")
                except httpx.HTTPStatusError as exc:
                    msg = exc.response.text[:500] if exc.response is not None else str(exc)
                    gh_meta["post_error"] = f"GitHub API {exc.response.status_code if exc.response else '?'}: {msg}"
                except ValueError as exc:
                    gh_meta["post_error"] = str(exc)
                except Exception as exc:  # noqa: BLE001
                    gh_meta["post_error"] = str(exc)
            if request_self_as_reviewer:
                try:
                    login = await github.get_auth_login()
                    if not login:
                        gh_meta["reviewer_error"] = "Could not resolve GitHub login for token."
                    else:
                        await github.request_reviewers(owner, repo, pull_number, [login])
                        gh_meta["requested_reviewer"] = login
                except httpx.HTTPStatusError as exc:
                    msg = exc.response.text[:300] if exc.response is not None else str(exc)
                    gh_meta["reviewer_error"] = f"GitHub API {exc.response.status_code if exc.response else '?'}: {msg}"
                except Exception as exc:  # noqa: BLE001
                    gh_meta["reviewer_error"] = str(exc)

    review_record["github"] = gh_meta
    return review_record
