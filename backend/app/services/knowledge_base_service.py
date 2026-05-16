"""Knowledge base ingestion + retrieval service.

Stores chunked documents and their embeddings in IBM Db2 via langchain-db2
when available; falls back to a simple in-process index when Db2 isn't
reachable (useful for local demos and CI).
"""

from __future__ import annotations

import asyncio
import logging
import math
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.core.config import get_settings
from app.services.embeddings_service import EmbeddingsService, get_embeddings_service

logger = logging.getLogger(__name__)
settings = get_settings()


# --------------------------------------------------------------------------- #
# Data model
# --------------------------------------------------------------------------- #


@dataclass
class DocumentRecord:
    """In-memory record describing an ingested document."""

    id: str
    title: str
    source: str
    content_type: str
    chunk_count: int
    created_at: datetime
    size_bytes: int
    tags: List[str] = field(default_factory=list)


@dataclass
class ChunkRecord:
    """In-memory record describing a single document chunk."""

    id: str
    document_id: str
    chunk_index: int
    content: str
    embedding: List[float]
    metadata: Dict[str, Any]


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _split_text(text: str, chunk_size: int = 800, overlap: int = 120) -> List[str]:
    """Split text into roughly fixed-size overlapping chunks.

    A character-based splitter keeps the pipeline self-contained while still
    producing reasonable RAG chunks for source code and markdown.
    """
    text = text.strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end]
        # Try to break on the last newline within the window for cleaner chunks.
        if end < len(text):
            last_newline = chunk.rfind("\n")
            if last_newline > chunk_size // 2:
                end = start + last_newline
                chunk = text[start:end]
        chunks.append(chunk.strip())
        if end >= len(text):
            break
        start = max(end - overlap, end)
    return [c for c in chunks if c]


def _cosine(a: List[float], b: List[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


# --------------------------------------------------------------------------- #
# Service
# --------------------------------------------------------------------------- #


class KnowledgeBaseService:
    """High-level knowledge base operations: ingest, list, search, delete."""

    def __init__(
        self,
        embeddings: Optional[EmbeddingsService] = None,
    ) -> None:
        self.embeddings = embeddings or get_embeddings_service()
        self._documents: Dict[str, DocumentRecord] = {}
        self._chunks: Dict[str, List[ChunkRecord]] = {}
        self._lock = asyncio.Lock()
        self._db2_store: Any = None
        self._backend: str = "inmemory"
        self._try_init_db2()

    # ------------------------------------------------------------------ #
    # Backend selection
    # ------------------------------------------------------------------ #

    def _try_init_db2(self) -> None:
        """Best-effort initialization of the Db2 vector store.

        We don't fail hard here so the demo can still run when the remote
        Db2 instance isn't reachable. The service reports its backend via
        `get_backend_info()`.
        """
        if settings.vector_db_type != "db2":
            logger.info("Knowledge base running with in-memory backend (vector_db_type=%s)", settings.vector_db_type)
            return
        try:
            from app.rag.db2_vector_store import Db2VectorStore  # noqa: WPS433
        except ImportError as exc:
            logger.warning("langchain-db2 not importable, falling back to in-memory KB: %s", exc)
            return

        try:
            self._db2_store = Db2VectorStore(
                database=settings.db2_database,
                hostname=settings.db2_hostname,
                port=settings.db2_port,
                protocol=settings.db2_protocol,
                uid=settings.db2_uid,
                pwd=settings.db2_pwd,
                schema=settings.db2_schema,
                table_name=f"{settings.db2_table_prefix}_KB",
                embedding_dimension=settings.embedding_dimension,
            )
            self._backend = "db2"
            logger.info("Knowledge base using IBM Db2 vector store")
        except Exception as exc:  # broad, intentionally
            logger.warning("Db2 vector store unavailable, using in-memory KB: %s", exc)
            self._db2_store = None

    def get_backend_info(self) -> Dict[str, Any]:
        """Expose KB backend metadata for the UI / status endpoint."""
        return {
            "backend": self._backend,
            "vector_db_type": settings.vector_db_type,
            "ollama_base_url": settings.ollama_base_url,
            "embedding_model": self.embeddings.model,
        }

    # ------------------------------------------------------------------ #
    # Mutations
    # ------------------------------------------------------------------ #

    async def ingest(
        self,
        title: str,
        content: str,
        source: str = "upload",
        content_type: str = "text/plain",
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Chunk + embed + store a document. Returns the created document record."""
        if not content.strip():
            raise ValueError("Document content is empty")

        document_id = str(uuid.uuid4())
        chunks = _split_text(content)
        if not chunks:
            raise ValueError("No text chunks produced from document")

        logger.info("Ingesting %s (%d chunks) via %s backend", title, len(chunks), self._backend)

        embeddings = await self.embeddings.embed_batch(chunks)

        chunk_records: List[ChunkRecord] = []
        for i, (chunk_text, vector) in enumerate(zip(chunks, embeddings)):
            chunk_records.append(
                ChunkRecord(
                    id=f"{document_id}:{i}",
                    document_id=document_id,
                    chunk_index=i,
                    content=chunk_text,
                    embedding=vector,
                    metadata={
                        "title": title,
                        "source": source,
                        "content_type": content_type,
                        "chunk_index": i,
                    },
                )
            )

        async with self._lock:
            self._documents[document_id] = DocumentRecord(
                id=document_id,
                title=title,
                source=source,
                content_type=content_type,
                chunk_count=len(chunk_records),
                created_at=datetime.now(timezone.utc),
                size_bytes=len(content.encode("utf-8")),
                tags=tags or [],
            )
            self._chunks[document_id] = chunk_records

        # Best-effort Db2 mirror — never blocks the demo on Db2 connectivity.
        if self._db2_store is not None:
            try:
                for chunk in chunk_records:
                    await self._db2_store.add(
                        document_id=chunk.id,
                        content=chunk.content,
                        embedding=chunk.embedding,
                        metadata=chunk.metadata,
                    )
            except Exception as exc:
                logger.warning("Db2 add failed, kept in-memory copy: %s", exc)

        return self._serialize_document(self._documents[document_id])

    async def delete(self, document_id: str) -> bool:
        async with self._lock:
            existed = document_id in self._documents
            self._documents.pop(document_id, None)
            chunks = self._chunks.pop(document_id, [])

        if self._db2_store is not None:
            for chunk in chunks:
                try:
                    await self._db2_store.delete(chunk.id)
                except Exception as exc:
                    logger.warning("Db2 delete failed for %s: %s", chunk.id, exc)
        return existed

    async def list_documents(self) -> List[Dict[str, Any]]:
        async with self._lock:
            return [self._serialize_document(d) for d in sorted(
                self._documents.values(),
                key=lambda d: d.created_at,
                reverse=True,
            )]

    # ------------------------------------------------------------------ #
    # Retrieval
    # ------------------------------------------------------------------ #

    async def search(self, query: str, limit: int = 4) -> List[Dict[str, Any]]:
        if not self._chunks:
            return []
        query_vec = await self.embeddings.embed(query)

        scored: List[Dict[str, Any]] = []
        for chunks in self._chunks.values():
            for chunk in chunks:
                score = _cosine(query_vec, chunk.embedding)
                if score <= 0:
                    continue
                scored.append({
                    "score": round(score, 4),
                    "content": chunk.content,
                    "document_id": chunk.document_id,
                    "chunk_index": chunk.chunk_index,
                    "metadata": chunk.metadata,
                })
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:limit]

    async def context_for(self, query: str, limit: int = 4) -> List[str]:
        """Return retrieved chunks as plain strings for agent prompts."""
        results = await self.search(query, limit=limit)
        return [
            f"[{r['metadata'].get('title', 'doc')} #{r['chunk_index']}] {r['content']}"
            for r in results
        ]

    # ------------------------------------------------------------------ #
    # Serialization
    # ------------------------------------------------------------------ #

    @staticmethod
    def _serialize_document(doc: DocumentRecord) -> Dict[str, Any]:
        return {
            "id": doc.id,
            "title": doc.title,
            "source": doc.source,
            "content_type": doc.content_type,
            "chunk_count": doc.chunk_count,
            "size_bytes": doc.size_bytes,
            "created_at": doc.created_at.isoformat(),
            "tags": doc.tags,
        }


_knowledge_base_service: Optional[KnowledgeBaseService] = None


def get_knowledge_base_service() -> KnowledgeBaseService:
    """Return the singleton knowledge base service."""
    global _knowledge_base_service
    if _knowledge_base_service is None:
        _knowledge_base_service = KnowledgeBaseService()
    return _knowledge_base_service


# Made with Bob
