"""Pull request API endpoints."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.ai_service import AIReviewService

router = APIRouter()

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

# Made with Bob
