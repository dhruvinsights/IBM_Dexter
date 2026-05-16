"""Runtime settings API.

Lets the UI inspect and update credentials (GitHub token, etc.) without
restarting the backend. Overrides are kept in-process only.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.core.runtime_config import get_runtime_config
from app.services.github_service import GitHubService
from app.services.knowledge_base_service import get_knowledge_base_service

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


class GithubTokenRequest(BaseModel):
    token: str = Field(..., min_length=10, description="Personal access token, fine-grained PAT, or OAuth token")
    verify: bool = True


class GithubTokenResponse(BaseModel):
    ok: bool
    login: Optional[str] = None
    scopes: Optional[str] = None
    masked_token: Optional[str] = None
    message: Optional[str] = None


@router.get("/settings")
async def get_runtime_settings() -> Dict[str, Any]:
    """Return masked runtime configuration plus key backend health signals."""
    rc = get_runtime_config()
    kb = get_knowledge_base_service()
    return {
        "llm": {
            "provider": settings.llm_provider,
            "model": settings.ollama_model,
            "base_url": settings.ollama_base_url,
        },
        "vector_db": {
            "type": settings.vector_db_type,
            "backend": kb.get_backend_info().get("backend"),
        },
        "github": {
            "configured": bool(rc.github_token()),
            "source": "runtime" if rc.has("github_token") else ("env" if settings.github_token else "none"),
        },
        "runtime_overrides": rc.snapshot(),
    }


@router.post("/settings/github-token", response_model=GithubTokenResponse)
async def update_github_token(payload: GithubTokenRequest) -> GithubTokenResponse:
    """Update GitHub PAT used by the backend, optionally verifying against GitHub."""
    token = payload.token.strip()
    if payload.verify:
        result = await GitHubService().verify_token(token=token)
        if not result.get("ok"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result.get("message") or "GitHub rejected the token",
            )
        get_runtime_config().set("github_token", token)
        return GithubTokenResponse(
            ok=True,
            login=result.get("login"),
            scopes=result.get("scopes"),
            masked_token=_mask(token),
            message=f"Verified as {result.get('login')}",
        )
    get_runtime_config().set("github_token", token)
    return GithubTokenResponse(ok=True, masked_token=_mask(token), message="Token stored (unverified)")


@router.delete(
    "/settings/github-token",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def clear_github_token() -> Response:
    get_runtime_config().set("github_token", None)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/settings/github/verify")
async def verify_github_token() -> Dict[str, Any]:
    """Verify the currently-configured GitHub token (runtime or env)."""
    return await GitHubService().verify_token()


def _mask(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 8:
        return "•" * len(value)
    return f"{value[:4]}…{value[-4:]}"


# Made with Bob
