"""Pull request API endpoints."""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, HttpUrl

from app.api.v1.endpoints.auth import require_api_user
from app.services.ai_service import AIReviewService
from app.services.app_state_persistence import load_pull_request_state, save_pull_request_state
from app.services.pr_review_runner import run_github_pr_review

logger = logging.getLogger(__name__)
router = APIRouter(dependencies=[Depends(require_api_user)])


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

def _default_pull_requests() -> Dict[int, Dict[str, Any]]:
    return {
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


_LOADED_PR, _LOADED_REV = load_pull_request_state()
_PULL_REQUESTS: Dict[int, Dict[str, Any]] = _LOADED_PR if _LOADED_PR else _default_pull_requests()
_REVIEWS: List[Dict[str, Any]] = list(_LOADED_REV)


def _persist_pr_state() -> None:
    save_pull_request_state(_PULL_REQUESTS, _REVIEWS)


def save_pr_analysis_record(review_record: Dict[str, Any]) -> None:
    """Append a completed GitHub PR analysis to persisted review history."""
    pr = review_record.get("pull_request") or {}
    num = pr.get("number")
    _REVIEWS.append({"pull_request_id": num, **review_record})
    _persist_pr_state()


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
    post_review_to_github: bool = Field(
        default=False,
        description="Submit a PR review comment (token needs pull_requests: write).",
    )
    request_self_as_reviewer: bool = Field(
        default=False,
        description="Request the authenticated GitHub user as a reviewer on the PR.",
    )
    inline_review_comments: bool = Field(
        default=True,
        description="When posting a GitHub review, add inline line comments (and suggestion blocks when available).",
    )


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
    _persist_pr_state()
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
    record = await run_github_pr_review(
        pr_ref["owner"],
        pr_ref["repo"],
        pr_ref["number"],
        use_rag=payload.use_rag,
        rag_query=payload.rag_query,
        rag_limit=payload.rag_limit,
        post_review_to_github=payload.post_review_to_github,
        request_self_as_reviewer=payload.request_self_as_reviewer,
        inline_review_comments=payload.inline_review_comments,
    )
    if not record.get("ok"):
        err = str(record.get("error") or "unknown")
        detail = str(record.get("detail") or err)
        if err == "github_http_error":
            code = int(record.get("status_code") or 502)
            if code in (401, 403):
                detail = (
                    "GitHub returned 401/403. Set DEXTER_GITHUB_TOKEN with a token that has "
                    "read access to this repository, or use a public PR."
                )
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)
        if err == "github_network":
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)

    save_pr_analysis_record(record)
    return record


# Made with Bob
