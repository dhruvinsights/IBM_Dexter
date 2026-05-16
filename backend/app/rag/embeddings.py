"""Embedding utilities for Dexter's RAG pipeline."""

from __future__ import annotations

import hashlib
from typing import Iterable


class EmbeddingService:
    """Provide deterministic placeholder embeddings for MVP development."""

    async def embed_text(self, text: str, dimensions: int = 16) -> list[float]:
        """Generate a deterministic embedding vector from input text."""
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        return [byte / 255 for byte in digest[:dimensions]]

    async def embed_documents(self, documents: Iterable[str], dimensions: int = 16) -> list[list[float]]:
        """Generate embeddings for multiple documents."""
        return [await self.embed_text(document, dimensions=dimensions) for document in documents]

# Made with Bob
