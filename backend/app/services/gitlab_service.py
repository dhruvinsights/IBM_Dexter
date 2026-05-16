"""GitLab integration service."""

from __future__ import annotations

import hashlib
import hmac
import logging
from typing import Any, Dict, Optional
from urllib.parse import quote_plus

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class GitLabService:
    """Provide GitLab API integration helpers."""

    def __init__(self) -> None:
        """Initialize the GitLab service client configuration."""
        self.base_url = "https://gitlab.com/api/v4"
        self.headers = {
            "PRIVATE-TOKEN": settings.gitlab_token,
            "Content-Type": "application/json",
        }

    async def fetch_pr_details(self, project_path: str, merge_request_iid: int) -> Dict[str, Any]:
        """Fetch merge request details from GitLab."""
        project = quote_plus(project_path)
        url = f"{self.base_url}/projects/{project}/merge_requests/{merge_request_iid}"
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_file_diffs(self, project_path: str, merge_request_iid: int) -> Dict[str, Any]:
        """Fetch merge request changes from GitLab."""
        project = quote_plus(project_path)
        url = f"{self.base_url}/projects/{project}/merge_requests/{merge_request_iid}/changes"
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def post_review_comment(self, project_path: str, merge_request_iid: int, body: str) -> Dict[str, Any]:
        """Post a note on a merge request."""
        project = quote_plus(project_path)
        url = f"{self.base_url}/projects/{project}/merge_requests/{merge_request_iid}/notes"
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(url, headers=self.headers, json={"body": body})
            response.raise_for_status()
            return response.json()

    def validate_webhook_signature(self, token: Optional[str]) -> bool:
        """Validate a GitLab webhook token."""
        if not token:
            return False
        is_valid = hmac.compare_digest(token, settings.gitlab_webhook_secret)
        if not is_valid:
            logger.warning("GitLab webhook token validation failed")
        return is_valid

# Made with Bob
