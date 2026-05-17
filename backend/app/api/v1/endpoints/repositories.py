"""Repository management API endpoints."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, HttpUrl

from app.core.config import get_settings
from app.services.app_state_persistence import load_repository_state, save_repository_state

router = APIRouter()
settings = get_settings()

_LOADED_REPOS, _LOADED_NEXT = load_repository_state()
_REPOSITORIES: Dict[int, Dict[str, Any]] = dict(_LOADED_REPOS)
_NEXT_ID = _LOADED_NEXT
if _REPOSITORIES:
    _NEXT_ID = max(_NEXT_ID, max(_REPOSITORIES.keys()) + 1)


def _persist_repo_state() -> None:
    save_repository_state(_REPOSITORIES, _NEXT_ID)


def github_auto_review_full_names() -> Set[str]:
    """Lowercase owner/repo keys for GitHub repos that should receive automatic reviews."""
    out: Set[str] = set()
    for r in _REPOSITORIES.values():
        if r.get("platform") != "github":
            continue
        if not r.get("is_active", True):
            continue
        if not r.get("auto_review_enabled", True):
            continue
        fn = str(r.get("full_name", "")).strip().lower()
        if fn:
            out.add(fn)
    return out


def _webhook_setup_model() -> Optional["WebhookSetupHints"]:
    base = (settings.dexter_api_public_url or "").strip().rstrip("/")
    if not base or not base.startswith("https://"):
        return None
    return WebhookSetupHints(
        webhook_url=f"{base}/api/v1/webhooks/github",
        instructions=(
            "In the GitHub repo → Settings → Webhooks, add a webhook with this URL, "
            "content type application/json, and the same secret as DEXTER_GITHUB_WEBHOOK_SECRET."
        ),
    )


class WebhookSetupHints(BaseModel):
    """Hints for wiring GitHub → Dexter (only when DEXTER_API_PUBLIC_URL is HTTPS)."""

    webhook_url: str
    events: List[str] = Field(default_factory=lambda: ["pull_request"])
    content_type: str = "application/json"
    instructions: str


class RepositoryCreate(BaseModel):
    """Repository creation payload."""

    name: str = Field(min_length=1)
    full_name: str = Field(min_length=1)
    url: HttpUrl
    owner_id: int
    platform: str = "github"
    is_active: bool = True
    auto_review_enabled: bool = Field(
        default=True,
        description="When true and platform is GitHub, Dexter runs on pull_request webhooks for this repo.",
    )
    settings: Dict[str, Any] = Field(default_factory=dict)


class RepositoryUpdate(BaseModel):
    """Repository update payload."""

    name: Optional[str] = None
    full_name: Optional[str] = None
    url: Optional[HttpUrl] = None
    platform: Optional[str] = None
    is_active: Optional[bool] = None
    auto_review_enabled: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None


class RepositoryResponse(BaseModel):
    """Repository response payload."""

    id: int
    name: str
    full_name: str
    url: HttpUrl
    owner_id: int
    platform: str
    is_active: bool
    auto_review_enabled: bool
    settings: Dict[str, Any]


class RepositoryCreateResponse(RepositoryResponse):
    webhook_setup: Optional[WebhookSetupHints] = None


@router.get("/repositories", response_model=List[RepositoryResponse])
async def list_repositories() -> List[RepositoryResponse]:
    """Return all registered repositories."""
    return [RepositoryResponse(**_normalize_repo_row(repository)) for repository in _REPOSITORIES.values()]


def _normalize_repo_row(row: Dict[str, Any]) -> Dict[str, Any]:
    data = dict(row)
    if "auto_review_enabled" not in data:
        data["auto_review_enabled"] = True
    return data


@router.post("/repositories", response_model=RepositoryCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_repository(payload: RepositoryCreate) -> RepositoryCreateResponse:
    """Create a repository record."""
    global _NEXT_ID
    repository = payload.model_dump(mode="json")
    repository["id"] = _NEXT_ID
    _REPOSITORIES[_NEXT_ID] = repository
    _NEXT_ID += 1
    _persist_repo_state()
    hints = _webhook_setup_model() if payload.platform == "github" and payload.auto_review_enabled else None
    return RepositoryCreateResponse(**_normalize_repo_row(repository), webhook_setup=hints)


@router.get("/repositories/{repository_id}", response_model=RepositoryResponse)
async def get_repository(repository_id: int) -> RepositoryResponse:
    """Return a single repository by identifier."""
    repository = _REPOSITORIES.get(repository_id)
    if not repository:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    return RepositoryResponse(**_normalize_repo_row(repository))


@router.put("/repositories/{repository_id}", response_model=RepositoryResponse)
async def update_repository(repository_id: int, payload: RepositoryUpdate) -> RepositoryResponse:
    """Update an existing repository record."""
    repository = _REPOSITORIES.get(repository_id)
    if not repository:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")

    updates = payload.model_dump(exclude_unset=True, mode="json")
    repository.update(updates)
    _REPOSITORIES[repository_id] = repository
    _persist_repo_state()
    return RepositoryResponse(**_normalize_repo_row(repository))


@router.delete("/repositories/{repository_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_repository(repository_id: int) -> None:
    """Delete a repository by identifier."""
    if repository_id not in _REPOSITORIES:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    del _REPOSITORIES[repository_id]
    _persist_repo_state()


# Made with Bob
