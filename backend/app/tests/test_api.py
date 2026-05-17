"""Initial API test coverage for backend foundation."""

from __future__ import annotations

from typing import Any

import hashlib
import hmac
import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.models.pull_request import PullRequest
from app.models.repository import Repository
from app.models.review import Review
from app.models.user import User

settings = get_settings()


def test_health_check(client) -> None:
    """Verify the health endpoint returns service metadata."""
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "IBM Dexter Backend"


def test_authentication_flow(client) -> None:
    """Verify register, login, refresh, and current-user endpoints."""
    register_response = client.post(
        "/api/v1/register",
        json={"email": "user@example.com", "password": "test-password"},
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/login",
        json={"email": "user@example.com", "password": "test-password"},
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    me_response = client.get(
        "/api/v1/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "user@example.com"

    refresh_response = client.post(
        "/api/v1/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    assert "access_token" in refresh_response.json()


def test_repository_crud(client, repository_payload) -> None:
    """Verify repository CRUD endpoints."""
    create_response = client.post("/api/v1/repositories", json=repository_payload)
    assert create_response.status_code == 201
    repository = create_response.json()
    repository_id = repository["id"]

    list_response = client.get("/api/v1/repositories")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    detail_response = client.get(f"/api/v1/repositories/{repository_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["full_name"] == "ibm/dexter"

    update_response = client.put(
        f"/api/v1/repositories/{repository_id}",
        json={"is_active": False},
    )
    assert update_response.status_code == 200
    assert update_response.json()["is_active"] is False

    delete_response = client.delete(f"/api/v1/repositories/{repository_id}")
    assert delete_response.status_code == 204


def test_pull_request_review_flow(client) -> None:
    """Verify pull request review execution and review listing."""
    response = client.post(
        "/api/v1/pull-requests/1/review",
        json={
            "diffs": [
                {
                    "filename": "app.py",
                    "patch": "password = 'secret'\n# delete record",
                }
            ],
            "context": ["Follow IBM secure coding standards."],
        },
    )
    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "completed"
    assert body["result"]["findings"]

    reviews_response = client.get("/api/v1/reviews")
    assert reviews_response.status_code == 200
    assert len(reviews_response.json()) == 1


def test_github_webhook_handling(client) -> None:
    """Verify GitHub webhook signature validation."""
    payload = b'{"action":"opened"}'
    signature = "sha256=" + hmac.new(
        settings.github_webhook_secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()

    response = client.post(
        "/api/v1/webhooks/github",
        content=payload,
        headers={"X-Hub-Signature-256": signature},
    )
    assert response.status_code == 200
    assert response.json()["provider"] == "github"


def test_gitlab_webhook_handling(client) -> None:
    """Verify GitLab webhook token validation."""
    response = client.post(
        "/api/v1/webhooks/gitlab",
        headers={"X-Gitlab-Token": settings.gitlab_webhook_secret},
    )
    assert response.status_code == 200
    assert response.json()["provider"] == "gitlab"


def test_repository_requires_auth_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
    repository_payload: dict[str, Any],
) -> None:
    """Protected routers reject unauthenticated calls when auth is required."""
    monkeypatch.setenv("DEXTER_REQUIRE_API_BEARER_AUTH", "true")
    get_settings.cache_clear()
    from main import app

    with TestClient(app) as client:
        response = client.post("/api/v1/repositories", json=repository_payload)
    assert response.status_code == 401


def test_repository_create_ok_with_api_key(
    monkeypatch: pytest.MonkeyPatch,
    repository_payload: dict[str, Any],
) -> None:
    monkeypatch.setenv("DEXTER_REQUIRE_API_BEARER_AUTH", "true")
    monkeypatch.setenv("DEXTER_API_KEY", "integration-test-api-key-32chars!")
    get_settings.cache_clear()
    from main import app

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/repositories",
            json=repository_payload,
            headers={"X-API-Key": "integration-test-api-key-32chars!"},
        )
    assert response.status_code == 201


def test_model_instantiation() -> None:
    """Verify ORM models can be instantiated with expected fields."""
    user = User(email="user@example.com", hashed_password="hashed")
    repository = Repository(
        name="dexter",
        full_name="ibm/dexter",
        url="https://github.com/ibm/dexter",
        owner_id=1,
        platform="github",
        is_active=True,
        settings={"default_branch": "main"},
    )
    pull_request = PullRequest(
        number=10,
        title="Add agent orchestration",
        description="Introduces the AI review coordinator",
        repository_id=1,
        author="developer",
        state="open",
    )
    review = Review(
        pull_request_id=1,
        status="pending",
        findings=[{"severity": "high"}],
        agent_results={"security-agent": {"summary": "ok"}},
        created_at=None,
        completed_at=None,
    )

    assert user.email == "user@example.com"
    assert repository.full_name == "ibm/dexter"
    assert pull_request.title == "Add agent orchestration"
    assert review.status == "pending"

# Made with Bob
