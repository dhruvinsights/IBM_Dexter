"""Pull request API endpoints."""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, HttpUrl

from app.services.ai_service import AIReviewService
from app.services.github_service import GitHubService
from app.services.knowledge_base_service import get_knowledge_base_service

logger = logging.getLogger(__name__)
router = APIRouter()


_GITHUB_PR_REGEX = re.compile(
    r"^https?://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/pull/(?P<number>\d+)(?:[/?#].*)?$"
)


def _parse_github_pr_url(url: str) -> Dict[str, Any]:
    match = _GITHUB_PR_REGEX.match(url.strip())
    if not match:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL must look like https://github.com/<owner>/<repo>/pull/<number>",
        )
    return {
        "owner": match["owner"],
        "repo": match["repo"],
        "number": int(match["number"]),
    }

_PULL_REQUESTS: Dict[int, Dict[str, Any]] = {
    1: {
        "id": 1,
        "number": 101,
        "title": "Initial backend foundation",
        "description": "Bootstrap IBM Dexter backend",
        "repository_id": 1,
        "author": "dexter-dev",
        "state": "open",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
}
_REVIEWS: List[Dict[str, Any]] = []


class PullRequestResponse(BaseModel):
    """Pull request response payload."""

    id: int
    number: int
    title: str
    description: Optional[str]
    repository_id: int
    author: str
    state: str
    created_at: datetime
    updated_at: datetime


class ReviewRequest(BaseModel):
    """Review execution request payload."""

    diffs: List[Dict[str, Any]] = Field(default_factory=list)
    context: List[str] = Field(default_factory=list)


class AnalyzeUrlRequest(BaseModel):
    """Request payload for analyzing a live GitHub PR by URL."""

    url: HttpUrl
    use_rag: bool = True
    rag_query: Optional[str] = None
    rag_limit: int = Field(default=4, ge=1, le=10)


@router.get("/pull-requests", response_model=List[PullRequestResponse])
async def list_pull_requests() -> List[PullRequestResponse]:
    """Return all tracked pull requests."""
    return [PullRequestResponse(**pull_request) for pull_request in _PULL_REQUESTS.values()]


@router.get("/pull-requests/{pull_request_id}", response_model=PullRequestResponse)
async def get_pull_request(pull_request_id: int) -> PullRequestResponse:
    """Return a single pull request by identifier."""
    pull_request = _PULL_REQUESTS.get(pull_request_id)
    if not pull_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pull request not found")
    return PullRequestResponse(**pull_request)


@router.post("/pull-requests/{pull_request_id}/review", status_code=status.HTTP_202_ACCEPTED)
async def review_pull_request(pull_request_id: int, payload: ReviewRequest) -> Dict[str, Any]:
    """Run the AI review workflow for a pull request."""
    pull_request = _PULL_REQUESTS.get(pull_request_id)
    if not pull_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pull request not found")

    review_service = AIReviewService()
    result = await review_service.review_code(
        pull_request=pull_request,
        diffs=payload.diffs,
        context=payload.context,
    )
    review_record = {
        "pull_request_id": pull_request_id,
        "status": result["status"],
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "result": result,
    }
    _REVIEWS.append(review_record)
    return review_record


@router.post("/pull-requests/analyze-url")
async def analyze_pull_request_url(payload: AnalyzeUrlRequest) -> Dict[str, Any]:
    """Fetch a live GitHub PR by URL and run the full agent pipeline.

    Steps:
      1. Parse owner / repo / number from URL
      2. Fetch PR metadata + file diffs via GitHub REST API
      3. Optionally retrieve RAG context from the knowledge base
      4. Run all configured review agents and return findings
    """
    pr_ref = _parse_github_pr_url(str(payload.url))
    github = GitHubService()

    try:
        pr_meta = await github.fetch_pr_details(pr_ref["owner"], pr_ref["repo"], pr_ref["number"])
        files = await github.get_file_diffs(pr_ref["owner"], pr_ref["repo"], pr_ref["number"])
    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code
        detail = exc.response.text[:200] if exc.response is not None else str(exc)
        if status_code in (401, 403):
            detail = (
                "GitHub returned 401/403. Set DEXTER_GITHUB_TOKEN with a token that has "
                "read access to this repository, or use a public PR."
            )
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Network error: {exc}")

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
        "repository": f"{pr_ref['owner']}/{pr_ref['repo']}",
    }

    rag_context: List[str] = []
    rag_meta: Dict[str, Any] = {"enabled": payload.use_rag, "retrieved": 0}
    if payload.use_rag:
        try:
            kb = get_knowledge_base_service()
            query = payload.rag_query or (pull_request.get("title") or "") + " " + (pull_request.get("description") or "")
            query = query.strip() or "code review best practices"
            rag_context = await kb.context_for(query, limit=payload.rag_limit)
            rag_meta["retrieved"] = len(rag_context)
            rag_meta["backend"] = kb.get_backend_info()
        except Exception as exc:
            logger.warning("RAG retrieval skipped: %s", exc)
            rag_meta["error"] = str(exc)

    review_service = AIReviewService()
    result = await review_service.review_code(
        pull_request=pull_request,
        diffs=diffs,
        context=rag_context,
    )

    review_record = {
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
    }
    _REVIEWS.append({
        "pull_request_id": pr_meta.get("number"),
        **review_record,
    })
    return review_record

# Made with Bob
