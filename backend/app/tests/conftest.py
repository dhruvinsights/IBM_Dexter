"""Shared pytest fixtures for backend API tests."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from typing import Any

# Force test-friendly AI + vector defaults before importing the FastAPI app (main.py caches Settings).
os.environ["DEXTER_LLM_PROVIDER"] = "openai"
os.environ["DEXTER_OPENAI_API_KEY"] = "sk-test-stub"
os.environ["DEXTER_EMBEDDING_PROVIDER"] = "ollama"
os.environ["DEXTER_VECTOR_DB_TYPE"] = "inmemory"
os.environ["DEXTER_APP_ENV"] = "test"

import pytest
from fastapi.testclient import TestClient

from app.api.v1.endpoints.auth import _USERS
from app.api.v1.endpoints.pull_requests import _REVIEWS
from app.api.v1.endpoints.repositories import _REPOSITORIES
from app.core.config import get_settings
from main import app

settings = get_settings()


@pytest.fixture(autouse=True)
def _stub_openai_chat_llm(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    """Prevent real HTTPS calls to api.openai.com during PR review tests."""
    if request.node.get_closest_marker("no_llm_stub"):
        return
    import app.services.llm_service as lm

    stub_payload = json.dumps(
        {
            "summary": "Stub LLM summary",
            "overall_severity": "medium",
            "findings": [
                {
                    "severity": "medium",
                    "file": "stub.py",
                    "line": 1,
                    "category": "stub",
                    "message": "Stub LLM finding",
                    "recommendation": "None",
                    "confidence": 0.5,
                }
            ],
        }
    )

    def _fake_call(self, prompt, stop=None, run_manager=None, **kwargs):
        return stub_payload

    monkeypatch.setattr(lm.OpenAIChatHTTPLLM, "_call", _fake_call)


@pytest.fixture(autouse=True)
def _stub_embeddings_health(monkeypatch: pytest.MonkeyPatch) -> None:
    """Knowledge-base status should not depend on a local Ollama daemon in CI."""
    from app.services.embeddings_service import EmbeddingsService

    async def _healthy(self) -> bool:
        return True

    monkeypatch.setattr(EmbeddingsService, "health", _healthy)


@pytest.fixture(autouse=True)
def reset_in_memory_stores() -> None:
    """Reset mutable in-memory stores between tests."""
    _USERS.clear()
    _REPOSITORIES.clear()
    _REVIEWS.clear()


@pytest.fixture(autouse=True)
def _clear_settings_lru_cache() -> None:
    """Reload Settings from env for each test (monkeypatch + resolver changes)."""
    get_settings.cache_clear()
    yield


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
