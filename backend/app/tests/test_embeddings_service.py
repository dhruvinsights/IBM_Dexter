"""EmbeddingsService HTTP behaviour (Ollama + OpenAI)."""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from app.core.config import get_settings
from app.services.embeddings_service import EmbeddingsService, reset_embeddings_service


@pytest.fixture(autouse=True)
def _reset_emb_singleton() -> None:
    reset_embeddings_service()
    yield
    reset_embeddings_service()


@respx.mock
@pytest.mark.asyncio
async def test_embed_ollama(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEXTER_EMBEDDING_PROVIDER", "ollama")
    monkeypatch.setenv("DEXTER_OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
    get_settings.cache_clear()
    respx.post("http://127.0.0.1:11434/api/embeddings").mock(
        return_value=Response(
            200,
            json={"embedding": [0.1, 0.2, 0.3]},
        )
    )

    class _RC:
        def ollama_base_url(self) -> str:
            return "http://127.0.0.1:11434"

    monkeypatch.setattr("app.services.embeddings_service.get_runtime_config", lambda: _RC())

    svc = EmbeddingsService()
    vec = await svc.embed("hello")
    assert vec == [0.1, 0.2, 0.3]


@respx.mock
@pytest.mark.asyncio
async def test_embed_openai(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEXTER_EMBEDDING_PROVIDER", "openai")
    monkeypatch.setenv("DEXTER_OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("DEXTER_OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    get_settings.cache_clear()
    respx.post("https://api.openai.com/v1/embeddings").mock(
        return_value=Response(
            200,
            json={"data": [{"embedding": [0.5, -0.5]}]},
        )
    )
    svc = EmbeddingsService()
    vec = await svc.embed("hello")
    assert vec == [0.5, -0.5]


@pytest.mark.asyncio
async def test_embed_openai_requires_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEXTER_EMBEDDING_PROVIDER", "openai")
    monkeypatch.delenv("DEXTER_OPENAI_API_KEY", raising=False)
    get_settings.cache_clear()
    svc = EmbeddingsService()
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        await svc.embed("x")
