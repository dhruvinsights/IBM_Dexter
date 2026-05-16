"""Retrieval orchestration for the Dexter RAG layer."""

from __future__ import annotations

from typing import Dict, List, Optional

from app.rag.embeddings import EmbeddingService
from app.rag.vector_store import InMemoryVectorStore


class RetrievalService:
    """Coordinate embedding generation and vector retrieval."""

    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        vector_store: Optional[InMemoryVectorStore] = None,
    ) -> None:
        """Initialize retrieval dependencies."""
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store = vector_store or InMemoryVectorStore()

    async def index_documents(self, documents: List[Dict[str, str]]) -> None:
        """Embed and store documents for later retrieval."""
        for document in documents:
            embedding = await self.embedding_service.embed_text(document["content"])
            await self.vector_store.add(
                document_id=document["id"],
                content=document["content"],
                embedding=embedding,
            )

    async def retrieve(self, query: str, limit: int = 5) -> List[str]:
        """Retrieve relevant document contents for a query."""
        query_embedding = await self.embedding_service.embed_text(query)
        matches = await self.vector_store.search(query_embedding, limit=limit)
        return [str(match["content"]) for match in matches]

# Made with Bob
