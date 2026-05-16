"""Repository management API endpoints."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, HttpUrl

router = APIRouter()

_REPOSITORIES: Dict[int, Dict[str, Any]] = {}
_NEXT_ID = 1


class RepositoryCreate(BaseModel):
    """Repository creation payload."""

    name: str = Field(min_length=1)
    full_name: str = Field(min_length=1)
    url: HttpUrl
    owner_id: int
    platform: str = "github"
    is_active: bool = True
    settings: Dict[str, Any] = Field(default_factory=dict)


class RepositoryUpdate(BaseModel):
    """Repository update payload."""

    name: Optional[str] = None
    full_name: Optional[str] = None
    url: Optional[HttpUrl] = None
    platform: Optional[str] = None
    is_active: Optional[bool] = None
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
    settings: Dict[str, Any]


@router.get("/repositories", response_model=List[RepositoryResponse])
async def list_repositories() -> List[RepositoryResponse]:
    """Return all registered repositories."""
    return [RepositoryResponse(**repository) for repository in _REPOSITORIES.values()]


@router.post("/repositories", response_model=RepositoryResponse, status_code=status.HTTP_201_CREATED)
async def create_repository(payload: RepositoryCreate) -> RepositoryResponse:
    """Create a repository record."""
    global _NEXT_ID
    repository = payload.model_dump()
    repository["id"] = _NEXT_ID
    _REPOSITORIES[_NEXT_ID] = repository
    _NEXT_ID += 1
    return RepositoryResponse(**repository)


@router.get("/repositories/{repository_id}", response_model=RepositoryResponse)
async def get_repository(repository_id: int) -> RepositoryResponse:
    """Return a single repository by identifier."""
    repository = _REPOSITORIES.get(repository_id)
    if not repository:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    return RepositoryResponse(**repository)


@router.put("/repositories/{repository_id}", response_model=RepositoryResponse)
async def update_repository(repository_id: int, payload: RepositoryUpdate) -> RepositoryResponse:
    """Update an existing repository record."""
    repository = _REPOSITORIES.get(repository_id)
    if not repository:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")

    updates = payload.model_dump(exclude_unset=True)
    repository.update(updates)
    _REPOSITORIES[repository_id] = repository
    return RepositoryResponse(**repository)


@router.delete("/repositories/{repository_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_repository(repository_id: int) -> None:
    """Delete a repository by identifier."""
    if repository_id not in _REPOSITORIES:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    del _REPOSITORIES[repository_id]

# Made with Bob
