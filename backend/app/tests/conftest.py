"""Shared pytest fixtures for backend API tests."""

from __future__ import annotations

import hashlib
import hmac
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api.v1.endpoints.auth import _USERS
from app.api.v1.endpoints.pull_requests import _REVIEWS
from app.api.v1.endpoints.repositories import _REPOSITORIES
from app.core.config import get_settings
from main import app

settings = get_settings()


@pytest.fixture(autouse=True)
def reset_in_memory_stores() -> None:
    """Reset mutable in-memory stores between tests."""
    _USERS.clear()
    _REPOSITORIES.clear()
    _REVIEWS.clear()


@pytest.fixture()
def client() -> TestClient:
    """Create a FastAPI test client."""
    return TestClient(app)


@pytest.fixture()
def registered_user(client: TestClient) -> dict[str, Any]:
    """Create and return a registered test user."""
    payload = {"email": "tester@example.com", "password": "strong-password"}
    response = client.post("/api/v1/register", json=payload)
    assert response.status_code == 201
    return response.json()


@pytest.fixture()
def auth_tokens(client: TestClient, registered_user: dict[str, Any]) -> dict[str, Any]:
    """Authenticate the registered user and return tokens."""
    response = client.post(
        "/api/v1/login",
        json={"email": registered_user["email"], "password": "strong-password"},
    )
    assert response.status_code == 200
    return response.json()


@pytest.fixture()
def repository_payload() -> dict[str, Any]:
    """Return a valid repository creation payload."""
    return {
        "name": "dexter",
        "full_name": "ibm/dexter",
        "url": "https://github.com/ibm/dexter",
        "owner_id": 1,
        "platform": "github",
        "is_active": True,
        "settings": {"auto_review": True},
    }


@pytest.fixture()
def github_signature() -> str:
    """Return a valid GitHub webhook signature for a fixed payload."""
    payload = b'{"action":"opened"}'
    digest = hmac.new(
        settings.github_webhook_secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()
    return f"sha256={digest}"


@pytest.fixture()
def github_payload() -> bytes:
    """Return a fixed GitHub webhook payload body."""
    return b'{"action":"opened"}'

# Made with Bob
