"""Review retrieval API endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints.pull_requests import _REVIEWS

router = APIRouter()


@router.get("/reviews")
async def list_reviews() -> list[dict]:
    """Return all recorded review runs."""
    return _REVIEWS

# Made with Bob
