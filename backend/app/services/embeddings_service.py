"""Embeddings service backed by Ollama (nomic-embed-text)."""

from __future__ import annotations

import logging
from typing import List, Optional

import httpx

from app.core.config import get_settings
from app.core.runtime_config import get_runtime_config

logger = logging.getLogger(__name__)
settings = get_settings()


class EmbeddingsService:
    """Generate embeddings via Ollama's HTTP API.

    Defaults to the `nomic-embed-text` model which produces 768-dim vectors.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: str = "nomic-embed-text",
        timeout: float = 30.0,
    ) -> None:
        self._base_url_override = base_url.strip().rstrip("/") if base_url else None
        self.model = model
        self.timeout = timeout

    def _base_url(self) -> str:
        if self._base_url_override:
            return self._base_url_override
        return get_runtime_config().ollama_base_url()

    async def embed(self, text: str) -> List[float]:
        """Return a single embedding vector for `text`."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self._base_url()}/api/embeddings",
                json={"model": self.model, "prompt": text},
            )
            response.raise_for_status()
            data = response.json()
            return data["embedding"]

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of texts sequentially (Ollama embeddings API is single-text)."""
        return [await self.embed(t) for t in texts]

    async def health(self) -> bool:
        """Quick health check against Ollama."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(f"{self._base_url()}/api/tags")
                return r.status_code == 200
        except Exception as exc:
            logger.warning("Embeddings backend unhealthy: %s", exc)
            return False


_embeddings_service: Optional[EmbeddingsService] = None


def get_embeddings_service() -> EmbeddingsService:
    """Return the singleton embeddings service."""
    global _embeddings_service
    if _embeddings_service is None:
        _embeddings_service = EmbeddingsService()
    return _embeddings_service


# Made with Bob
