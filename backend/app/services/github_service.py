"""GitHub integration service."""

from __future__ import annotations

import hashlib
import hmac
import logging
from typing import Any, Dict, List, Optional  # noqa: F401

import httpx

from app.core.config import get_settings
from app.core.runtime_config import get_runtime_config

logger = logging.getLogger(__name__)
settings = get_settings()


class GitHubService:
    """Provide GitHub API integration helpers."""

    def __init__(self) -> None:
        """Initialize the GitHub service client configuration.

        Token resolution order: runtime override (set via Settings UI) →
        DEXTER_GITHUB_TOKEN env var. Tokens whose values look like the
        placeholder strings in .env.example are ignored.
        """
        self.base_url = "https://api.github.com"
        self.headers: Dict[str, str] = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        token = (get_runtime_config().github_token() or "").strip()
        if token and not token.lower().startswith("your_"):
            self.headers["Authorization"] = f"Bearer {token}"
            logger.info("GitHub client configured with auth token")
        else:
            logger.info("GitHub client configured for unauthenticated public access")

    async def verify_token(self, token: Optional[str] = None) -> Dict[str, Any]:
        """Verify a GitHub token by calling /user. Returns metadata or raises."""
        token = (token or get_runtime_config().github_token() or "").strip()
        if not token:
            return {"ok": False, "reason": "no_token"}
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{self.base_url}/user", headers=headers)
            if response.status_code == 200:
                data = response.json()
                return {
                    "ok": True,
                    "login": data.get("login"),
                    "name": data.get("name"),
                    "avatar_url": data.get("avatar_url"),
                    "scopes": response.headers.get("x-oauth-scopes", ""),
                }
            return {
                "ok": False,
                "reason": "rejected_by_github",
                "status_code": response.status_code,
                "message": (response.json() or {}).get("message", response.text[:200]),
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
