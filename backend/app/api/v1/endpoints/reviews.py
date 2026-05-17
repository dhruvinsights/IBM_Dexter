"""Review retrieval API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.v1.endpoints.auth import require_api_user
from app.api.v1.endpoints.pull_requests import _REVIEWS

router = APIRouter(dependencies=[Depends(require_api_user)])


@router.get("/reviews")
async def list_reviews() -> list[dict]:
    """Return all recorded review runs."""
    return _REVIEWS

# Made with Bob
