"""Embeddings for RAG: Ollama HTTP or OpenAI HTTP (no extra LangChain pins for embeddings)."""

from __future__ import annotations

import logging
from typing import List, Optional

import httpx

from app.core.config import get_settings
from app.core.runtime_config import get_runtime_config

logger = logging.getLogger(__name__)


class EmbeddingsService:
    """Generate embeddings via OpenAI or Ollama REST."""

    def __init__(
        self,
        timeout: float = 60.0,
    ) -> None:
        self.timeout = timeout

    def _ollama_base_url(self) -> str:
        return get_runtime_config().ollama_base_url().rstrip("/")

    async def embed(self, text: str) -> List[float]:
        """Return a single embedding vector for `text`."""
        settings = get_settings()
        prov = (settings.embedding_provider or "openai").lower()
        if prov == "openai":
            return await self._embed_openai(text)
        if prov == "ollama":
            return await self._embed_ollama(text)
        raise ValueError(f"Unsupported embedding provider: {settings.embedding_provider}")

    async def _embed_ollama(self, text: str) -> List[float]:
        settings = get_settings()
        model = settings.ollama_embedding_model
        root = self._ollama_base_url()
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{root}/api/embeddings",
                json={"model": model, "prompt": text},
            )
            response.raise_for_status()
            data = response.json()
        return data["embedding"]

    async def _embed_openai(self, text: str) -> List[float]:
        settings = get_settings()
        key = (settings.openai_api_key or "").strip()
        if not key:
            raise RuntimeError(
                "DEXTER_EMBEDDING_PROVIDER=openai requires DEXTER_OPENAI_API_KEY. "
                "Use embedding_provider=ollama for local Ollama-only setups."
            )
        model = settings.openai_embedding_model
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={"model": model, "input": text},
            )
            response.raise_for_status()
            data = response.json()
        return data["data"][0]["embedding"]

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed texts sequentially (simple + predictable for dimension checks)."""
        return [await self.embed(t) for t in texts]

    async def health(self) -> bool:
        """Quick health check for the configured embedding backend."""
        settings = get_settings()
        prov = (settings.embedding_provider or "openai").lower()
        try:
            if prov == "openai":
                return bool((settings.openai_api_key or "").strip())
            if prov == "ollama":
                async with httpx.AsyncClient(timeout=5.0) as client:
                    r = await client.get(f"{self._ollama_base_url()}/api/tags")
                    return r.status_code == 200
        except Exception as exc:
            logger.warning("Embeddings backend unhealthy: %s", exc)
            return False
        return False


_embeddings_service: Optional[EmbeddingsService] = None


def get_embeddings_service() -> EmbeddingsService:
    """Return the singleton embeddings service."""
    global _embeddings_service
    if _embeddings_service is None:
        _embeddings_service = EmbeddingsService()
    return _embeddings_service


def reset_embeddings_service() -> None:
    """Test helper: drop singleton between tests."""
    global _embeddings_service
    _embeddings_service = None


# Made with Bob
