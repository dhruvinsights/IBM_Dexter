"""Runtime settings API.

Lets the UI inspect and update credentials (GitHub token, etc.) without
restarting the backend. Overrides are kept in-process only.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.core.runtime_config import get_runtime_config
from app.services.github_service import GitHubService
from app.services.db2_runtime_settings import (
    db2_kb_storage_target,
    kb_table_prefix,
    test_db2_cli_connection,
)
from app.services.knowledge_base_service import get_knowledge_base_service, reset_knowledge_base_service
from app.services.llm_service import get_llm_service

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


class OllamaSettingsPayload(BaseModel):
    """Runtime Ollama URL/model overrides (in-memory only)."""

    base_url: Optional[str] = Field(default=None, description="Ollama root URL, e.g. http://localhost:11434")
    model: Optional[str] = Field(default=None, description="Ollama model tag, e.g. qwen2.5-coder:14b")


class Db2TestRequest(BaseModel):
    """Db2 CLI connection string to validate (ibm_db probe)."""

    connection_string: str = Field(..., min_length=8, description="e.g. DATABASE=u;HOSTNAME=h;PORT=50000;UID=u;PWD=p;")


class Db2SaveRequest(BaseModel):
    """Persist a Db2 CLI string at runtime (merged with DEXTER_DB2_* from .env for missing parts)."""

    connection_string: str = Field(..., min_length=8)
    kb_table_prefix: Optional[str] = Field(
        default=None,
        description="KB table stem: if it ends with _KB it is the full table name; else {stem}_KB (e.g. DEXTER → DEXTER_KB).",
    )
    db2_schema: str = Field(
        default="",
        description="Optional runtime schema override; empty clears override (uses DEXTER_DB2_SCHEMA).",
    )


def _normalize_kb_table_prefix(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    s = str(value).strip()
    return s or None


def _normalize_base_url(url: Optional[str]) -> str:
    if not url:
        return ""
    return str(url).strip().rstrip("/")


def _fetch_ollama_tags(base_url: str) -> List[str]:
    root = _normalize_base_url(base_url)
    if not root:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ollama base URL is required")
    try:
        response = httpx.get(f"{root}/api/tags", timeout=15.0)
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Could not reach Ollama at {root}: {exc}",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Invalid JSON from Ollama: {exc}",
        ) from exc

    models: List[str] = []
    for item in data.get("models") or []:
        name = item.get("name")
        if name:
            models.append(name)
    return models


@router.get("/settings")
async def get_runtime_settings() -> Dict[str, Any]:
    """Return masked runtime configuration plus key backend health signals."""
    rc = get_runtime_config()
    kb = get_knowledge_base_service()
    vdb = await kb.get_vector_db_status()
    return {
        "llm": {
            "provider": settings.llm_provider,
            "model": rc.ollama_model(),
            "base_url": rc.ollama_base_url(),
            "sources": {
                "model": "runtime" if rc.has("ollama_model") else "env",
                "base_url": "runtime" if rc.has("ollama_base_url") else "env",
            },
        },
        "vector_db": {
            "type": settings.vector_db_type,
            "backend": kb.get_backend_info().get("backend"),
            "reachable": vdb.get("reachable"),
            "error": vdb.get("error"),
            "detail": vdb.get("detail"),
            "configured_type": vdb.get("configured_type"),
            "kb_store_backend": vdb.get("kb_store_backend"),
            "db2_runtime_connection": rc.has("db2_connection_string"),
            "db2_kb_table_prefix": kb_table_prefix(rc),
            **db2_kb_storage_target(rc),
        },
        "github": {
            "configured": bool(rc.github_token()),
            "source": "runtime" if rc.has("github_token") else ("env" if settings.github_token else "none"),
        },
        "runtime_overrides": rc.snapshot(),
    }


@router.get("/settings/ollama/tags")
async def list_ollama_tags(base_url: Optional[str] = None) -> Dict[str, Any]:
    """Proxy Ollama /api/tags so the UI can populate model choices."""
    rc = get_runtime_config()
    resolved = _normalize_base_url(base_url) or rc.ollama_base_url()
    models = _fetch_ollama_tags(resolved)
    return {"ok": True, "base_url": resolved, "models": models}


@router.get("/settings/ollama/health")
async def ollama_health(base_url: Optional[str] = None) -> Dict[str, Any]:
    """Check that Ollama responds at the configured or provided URL."""
    rc = get_runtime_config()
    resolved = _normalize_base_url(base_url) or rc.ollama_base_url()
    models = _fetch_ollama_tags(resolved)
    return {"ok": True, "base_url": resolved, "model_count": len(models)}


@router.post("/settings/ollama")
async def update_ollama_settings(payload: OllamaSettingsPayload) -> Dict[str, Any]:
    """Apply runtime Ollama overrides and refresh the in-process LLM client."""
    rc = get_runtime_config()
    if payload.base_url is not None:
        normalized = _normalize_base_url(payload.base_url)
        rc.set("ollama_base_url", normalized or None)
    if payload.model is not None:
        rc.set("ollama_model", payload.model.strip() or None)
    get_llm_service().refresh_ollama_configuration()
    return {
        "ok": True,
        "llm": {
            "model": rc.ollama_model(),
            "base_url": rc.ollama_base_url(),
        },
    }


@router.post("/settings/db2/test")
async def test_db2_connection(payload: Db2TestRequest) -> Dict[str, Any]:
    """Run a read-only ibm_db probe against the provided CLI connection string."""
    result = await asyncio.to_thread(test_db2_cli_connection, payload.connection_string.strip())
    if not result.get("ok"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error") or "Db2 connection test failed",
        )
    return {"ok": True, "message": "Db2 accepted the connection (SELECT 1 ok).", "error": None}


@router.post("/settings/db2")
async def save_db2_connection(payload: Db2SaveRequest) -> Dict[str, Any]:
    """Store Db2 CLI string + optional KB table prefix, then reload the knowledge base service."""
    raw = payload.connection_string.strip()
    check = await asyncio.to_thread(test_db2_cli_connection, raw)
    if not check.get("ok"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=check.get("error") or "Db2 connection test failed; not saving.",
        )
    rc = get_runtime_config()
    rc.set("db2_connection_string", raw)
    prefix = _normalize_kb_table_prefix(payload.kb_table_prefix)
    if prefix is not None:
        rc.set("db2_kb_table_prefix", prefix)
    rc.set("db2_schema", payload.db2_schema.strip() or None)
    reset_knowledge_base_service()
    get_knowledge_base_service()
    return {
        "ok": True,
        "message": "Db2 connection saved. Knowledge base reloaded.",
        "kb_table_prefix": kb_table_prefix(rc),
    }


@router.delete("/settings/db2")
async def clear_db2_runtime_connection() -> Dict[str, Any]:
    """Remove runtime Db2 CLI override (falls back to DEXTER_DB2_* only)."""
    rc = get_runtime_config()
    rc.set("db2_connection_string", None)
    rc.set("db2_kb_table_prefix", None)
    rc.set("db2_schema", None)
    reset_knowledge_base_service()
    get_knowledge_base_service()
    return {"ok": True, "message": "Runtime Db2 connection cleared."}


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
