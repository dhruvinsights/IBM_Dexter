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

    async def get_auth_login(self) -> Optional[str]:
        """Return GitHub login for the current token, or None if unauthenticated."""
        if "Authorization" not in self.headers:
            return None
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(f"{self.base_url}/user", headers=self.headers)
            if response.status_code != 200:
                return None
            return response.json().get("login")

    async def request_reviewers(
        self, owner: str, repo: str, pull_number: int, reviewers: List[str]
    ) -> Dict[str, Any]:
        """Request users as reviewers on a pull request."""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers"
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(url, headers=self.headers, json={"reviewers": reviewers})
            response.raise_for_status()
            return response.json()

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

    async def get_file_content_at_commit(
        self, owner: str, repo: str, path: str, sha: str
    ) -> Optional[str]:
        """Fetch complete file content at a specific commit.
        
        This method retrieves the full file content (not just diffs) which is
        essential for AI agents to understand the complete context around changes.
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: File path within the repository
            sha: Commit SHA to fetch the file at
            
        Returns:
            Complete file content as string, or None if file doesn't exist
        """
        import base64
        
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        async with httpx.AsyncClient(timeout=20.0) as client:
            try:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params={'ref': sha}
                )
                if response.status_code == 404:
                    logger.debug(f"File not found: {path} at {sha}")
                    return None
                response.raise_for_status()
                data = response.json()
                
                # GitHub returns file content as base64-encoded
                if 'content' in data:
                    content_b64 = data['content'].replace('\n', '')
                    return base64.b64decode(content_b64).decode('utf-8', errors='replace')
                return None
            except Exception as exc:
                logger.warning(f"Failed to fetch content for {path}: {exc}")
                return None

    async def post_review_comments(
        self,
        owner: str,
        repo: str,
        pull_number: int,
        body: str,
        *,
        commit_id: Optional[str] = None,
        comments: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Post a pull request review: summary body plus optional inline comments (requires commit_id)."""
        payload: Dict[str, Any] = {"body": body, "event": "COMMENT"}
        if comments:
            if not commit_id:
                raise ValueError("commit_id is required when posting inline review comments")
            payload["commit_id"] = commit_id
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
