"""GET /settings exposes embeddings + deployment hints."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_settings_has_embeddings_and_deployment(client: TestClient) -> None:
    r = client.get("/api/v1/settings")
    assert r.status_code == 200
    body = r.json()
    assert "embeddings" in body
    assert body["embeddings"].get("provider")
    assert body["embeddings"].get("model")
    assert "deployment" in body
    assert "hosted_ollama_notice" in body["deployment"]
    assert "llm" in body
    assert "runtime" in body["llm"]
