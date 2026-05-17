"""Authentication API endpoints."""

from __future__ import annotations

import hmac
from datetime import datetime, timezone
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr

from app.core.config import get_settings
from app.core.security import (
    api_key_scheme,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    oauth2_scheme,
    validate_token_type,
    verify_password,
)

optional_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/login", auto_error=False)

router = APIRouter()

_USERS: dict[str, dict[str, object]] = {}


class RegisterRequest(BaseModel):
    """User registration payload."""

    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    """User login payload."""

    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    """Token refresh payload."""

    refresh_token: str


class TokenResponse(BaseModel):
    """Authentication token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Authenticated user response."""

    email: EmailStr
    is_active: bool
    is_superuser: bool
    created_at: datetime


def _get_current_user_payload(token: Annotated[str, Depends(oauth2_scheme)]) -> dict[str, object]:
    """Resolve the current user from a bearer token."""
    payload = decode_token(token)
    validate_token_type(payload, "access")
    email = str(payload.get("sub", ""))
    user = _USERS.get(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest) -> UserResponse:
    """Register a new user account."""
    email = payload.email.lower()
    if email in _USERS:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    user = {
        "email": email,
        "hashed_password": hash_password(payload.password),
        "is_active": True,
        "is_superuser": False,
        "created_at": datetime.now(timezone.utc),
    }
    _USERS[email] = user
    return UserResponse(**user)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest) -> TokenResponse:
    """Authenticate a user and issue tokens."""
    email = payload.email.lower()
    user = _USERS.get(email)
    if not user or not verify_password(payload.password, str(user["hashed_password"])):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return TokenResponse(
        access_token=create_access_token(email),
        refresh_token=create_refresh_token(email),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(payload: RefreshRequest) -> TokenResponse:
    """Exchange a refresh token for a new access token pair."""
    token_payload = decode_token(payload.refresh_token)
    validate_token_type(token_payload, "refresh")
    email = str(token_payload.get("sub", ""))
    if email not in _USERS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return TokenResponse(
        access_token=create_access_token(email),
        refresh_token=create_refresh_token(email),
    )


@router.get("/me", response_model=UserResponse)
async def read_me(current_user: Annotated[dict[str, object], Depends(_get_current_user_payload)]) -> UserResponse:
    """Return the currently authenticated user."""
    return UserResponse(**current_user)


async def require_api_user(
    token: Annotated[Optional[str], Depends(optional_oauth2)],
    api_key: Annotated[Optional[str], Security(api_key_scheme)],
) -> None:
    """Protect data-plane routes when DEXTER_REQUIRE_API_BEARER_AUTH=true.

    Accepts either a valid JWT access token or a valid ``X-API-Key`` matching ``DEXTER_API_KEY``.
    """
    settings = get_settings()
    if not settings.require_api_bearer_auth:
        return None
    if api_key and hmac.compare_digest(api_key, settings.api_key):
        return None
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    payload = decode_token(token)
    validate_token_type(payload, "access")
    email = str(payload.get("sub", ""))
    if email not in _USERS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return None


# Made with Bob
