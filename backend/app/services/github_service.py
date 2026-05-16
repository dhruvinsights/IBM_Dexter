"""GitHub integration service."""

from __future__ import annotations

import hashlib
import hmac
import logging
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class GitHubService:
    """Provide GitHub API integration helpers."""

    def __init__(self) -> None:
        """Initialize the GitHub service client configuration."""
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {settings.github_token}" if settings.github_token else "",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def fetch_pr_details(self, owner: str, repo: str, pull_number: int) -> Dict[str, Any]:
        """Fetch pull request details from GitHub."""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pull_number}"
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_file_diffs(self, owner: str, repo: str, pull_number: int) -> List[Dict[str, Any]]:
        """Fetch file diffs for a pull request."""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pull_number}/files"
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def post_review_comments(
        self,
        owner: str,
        repo: str,
        pull_number: int,
        body: str,
        comments: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Post a pull request review comment summary."""
        payload: Dict[str, Any] = {"body": body, "event": "COMMENT"}
        if comments:
            payload["comments"] = comments
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pull_number}/reviews"
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()

    def validate_webhook_signature(self, payload: bytes, signature: Optional[str]) -> bool:
        """Validate a GitHub webhook payload signature."""
        if not signature:
            return False
        expected = "sha256=" + hmac.new(
            settings.github_webhook_secret.encode("utf-8"),
            payload,
            hashlib.sha256,
        ).hexdigest()
        is_valid = hmac.compare_digest(expected, signature)
        if not is_valid:
            logger.warning("GitHub webhook signature validation failed")
        return is_valid

# Made with Bob
