"""Webhook ingestion API endpoints."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request, status

from app.api.v1.endpoints.repositories import github_auto_review_full_names
from app.api.v1.endpoints.pull_requests import save_pr_analysis_record
from app.services.github_service import GitHubService
from app.services.gitlab_service import GitLabService
from app.services.pr_review_runner import run_github_pr_review

router = APIRouter()
logger = logging.getLogger(__name__)

github_service = GitHubService()
gitlab_service = GitLabService()

_AUTO_ACTIONS = frozenset({"opened", "synchronize", "reopened", "ready_for_review"})


async def _run_auto_pr_review(owner: str, repo: str, pull_number: int, head_sha: str) -> None:
    try:
        record = await run_github_pr_review(
            owner,
            repo,
            pull_number,
            head_sha=head_sha,
            use_rag=True,
            rag_limit=4,
            post_review_to_github=True,
            request_self_as_reviewer=True,
            inline_review_comments=True,
            max_inline_comments=40,
        )
        if not record.get("ok"):
            logger.warning(
                "Auto PR review failed for %s/%s#%s: %s",
                owner,
                repo,
                pull_number,
                record.get("detail") or record.get("error"),
            )
            return
        save_pr_analysis_record(record)
        logger.info(
            "Auto PR review finished for %s/%s#%s (review posted: %s)",
            owner,
            repo,
            pull_number,
            record.get("github", {}).get("posted_review"),
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Auto PR review crashed for %s/%s#%s: %s", owner, repo, pull_number, exc)


@router.post("/webhooks/github")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: Optional[str] = Header(default=None),
    x_github_event: Optional[str] = Header(default=None),
) -> Dict[str, str]:
    """Receive and validate GitHub webhook events."""
    payload = await request.body()
    if not github_service.validate_webhook_signature(payload, x_hub_signature_256):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid GitHub signature")

    event = (x_github_event or "").strip().lower()
    if event != "pull_request":
        return {"status": "accepted", "provider": "github", "handled": "ignored"}

    try:
        data: Dict[str, Any] = json.loads(payload.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON payload")

    action = str(data.get("action") or "")
    if action not in _AUTO_ACTIONS:
        return {"status": "accepted", "provider": "github", "handled": "noop"}

    repo_block = data.get("repository") or {}
    full_name = str(repo_block.get("full_name") or "").strip().lower()
    if not full_name or full_name not in github_auto_review_full_names():
        return {"status": "accepted", "provider": "github", "handled": "unregistered"}

    pr = data.get("pull_request") or {}
    pr_number = pr.get("number")
    head = pr.get("head") or {}
    head_sha = str(head.get("sha") or "")
    if not isinstance(pr_number, int) or not head_sha:
        return {"status": "accepted", "provider": "github", "handled": "incomplete"}

    owner, repo = full_name.split("/", 1)
    background_tasks.add_task(_run_auto_pr_review, owner, repo, pr_number, head_sha)
    return {"status": "accepted", "provider": "github", "handled": "queued"}


@router.post("/webhooks/gitlab")
async def gitlab_webhook(
    x_gitlab_token: Optional[str] = Header(default=None),
) -> Dict[str, str]:
    """Receive and validate GitLab webhook events."""
    if not gitlab_service.validate_webhook_signature(x_gitlab_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid GitLab token")
    return {"status": "accepted", "provider": "gitlab"}

# Made with Bob
