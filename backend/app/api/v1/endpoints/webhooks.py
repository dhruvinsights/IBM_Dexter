"""Webhook ingestion API endpoints."""

from __future__ import annotations

from typing import Dict, Optional

from fastapi import APIRouter, Header, HTTPException, Request, status

from app.services.github_service import GitHubService
from app.services.gitlab_service import GitLabService

router = APIRouter()

github_service = GitHubService()
gitlab_service = GitLabService()


@router.post("/webhooks/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(default=None),
) -> Dict[str, str]:
    """Receive and validate GitHub webhook events."""
    payload = await request.body()
    if not github_service.validate_webhook_signature(payload, x_hub_signature_256):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid GitHub signature")
    return {"status": "accepted", "provider": "github"}


@router.post("/webhooks/gitlab")
async def gitlab_webhook(
    x_gitlab_token: Optional[str] = Header(default=None),
) -> Dict[str, str]:
    """Receive and validate GitLab webhook events."""
    if not gitlab_service.validate_webhook_signature(x_gitlab_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid GitLab token")
    return {"status": "accepted", "provider": "gitlab"}

# Made with Bob
