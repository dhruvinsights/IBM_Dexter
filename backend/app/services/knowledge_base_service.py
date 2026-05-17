"""Knowledge base ingestion + retrieval service.

Stores chunked documents and their embeddings in IBM Db2 via langchain-db2
when available; falls back to a simple in-process index when Db2 isn't
reachable (useful for local demos and CI).
"""

from __future__ import annotations

import asyncio
import logging
import math
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.core.config import get_settings
from app.core.data_dir import get_data_dir
from app.core.runtime_config import get_runtime_config
from app.services.effective_ai_config import embedding_runtime_summary
from app.services.embeddings_service import EmbeddingsService, get_embeddings_service
from app.services.kb_store_sqlite import delete_document as kb_sqlite_delete_document
from app.services.kb_store_sqlite import load_all as kb_sqlite_load_all
from app.services.kb_store_sqlite import replace_document as kb_sqlite_replace_document
from app.services.db2_runtime_settings import (
    create_db2_vector_store,
    db2_kb_storage_target,
    kb_vector_table_name,
)

logger = logging.getLogger(__name__)
settings = get_settings()

_VECTOR_DB_PROBE_TTL_SEC = 15.0


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


def _parse_created_at(raw: str) -> datetime:
    normalized = raw.replace("Z", "+00:00") if raw.endswith("Z") else raw
    return datetime.fromisoformat(normalized)


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
        self._sqlite_path = get_data_dir() / "knowledge_base.sqlite"
        self._vector_db_probe_lock = asyncio.Lock()
        self._vector_db_probe_cache: Optional[Dict[str, Any]] = None
        self._vector_db_probe_monotonic: float = 0.0
        self._hydrate_from_sqlite()
        self._try_init_db2()

    def _hydrate_from_sqlite(self) -> None:
        docs_payload, chunks_map = kb_sqlite_load_all(self._sqlite_path)
        for d in docs_payload:
            created_at = _parse_created_at(d["created_at"]) if isinstance(d["created_at"], str) else d["created_at"]
            self._documents[d["id"]] = DocumentRecord(
                id=d["id"],
                title=d["title"],
                source=d["source"],
                content_type=d["content_type"],
                chunk_count=int(d["chunk_count"]),
                created_at=created_at,
                size_bytes=int(d["size_bytes"]),
                tags=list(d.get("tags") or []),
            )
        for did, rows in chunks_map.items():
            chunk_recs: List[ChunkRecord] = []
            for c in rows:
                chunk_recs.append(
                    ChunkRecord(
                        id=c["id"],
                        document_id=c["document_id"],
                        chunk_index=int(c["chunk_index"]),
                        content=c["content"],
                        embedding=list(c["embedding"]),
                        metadata=dict(c["metadata"]),
                    )
                )
            self._chunks[did] = chunk_recs
        if self._documents:
            logger.info("Restored %d knowledge-base document(s) from SQLite", len(self._documents))

    def _persist_sqlite(self, doc: DocumentRecord, chunk_records: List[ChunkRecord]) -> None:
        payload = self._serialize_document(doc)
        chunk_dicts = [
            {
                "id": ch.id,
                "document_id": ch.document_id,
                "chunk_index": ch.chunk_index,
                "content": ch.content,
                "embedding": ch.embedding,
                "metadata": ch.metadata,
            }
            for ch in chunk_records
        ]
        kb_sqlite_replace_document(self._sqlite_path, payload, chunk_dicts)

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
            rc = get_runtime_config()
            table = kb_vector_table_name(rc)
            self._db2_store = create_db2_vector_store(table_name=table)
            self._backend = "db2"
            target = db2_kb_storage_target(rc)
            logger.info(
                "Knowledge base using IBM Db2 vector store (%s)",
                target.get("db2_kb_qualified_table"),
            )
        except Exception as exc:  # broad, intentionally
            logger.warning("Db2 vector store unavailable, using in-memory KB: %s", exc)
            self._db2_store = None

    def _probe_vector_db_sync(self) -> Dict[str, Any]:
        """Synchronous vector DB connectivity probe (run in a thread pool)."""
        vtype = (settings.vector_db_type or "inmemory").lower()
        rc = get_runtime_config()
        out: Dict[str, Any] = {
            "configured_type": vtype,
            "kb_store_backend": self._backend,
            "reachable": True,
            "error": None,
            "detail": "",
        }
        if vtype == "db2":
            out.update(db2_kb_storage_target(rc))
        if vtype == "inmemory":
            out["detail"] = "DEXTER_VECTOR_DB_TYPE=inmemory — no remote vector database."
            return out
        if vtype != "db2":
            out["detail"] = f"Vector DB type '{vtype}' — no TCP probe implemented."
            return out
        if self._db2_store is None:
            out["reachable"] = False
            out["error"] = (
                "Db2 client not initialized (missing dependency, import error, or constructor failure)."
            )
            out["detail"] = out["error"]
            return out
        ok, err = self._db2_store.verify_connectivity()
        out["reachable"] = ok
        out["error"] = err
        cat = out.get("db2_database_catalog") or settings.db2_database
        qual = out.get("db2_kb_qualified_table") or ""
        out["detail"] = (
            f"Db2 OK — catalog {cat}, KB {qual} ({settings.db2_hostname}:{settings.db2_port})."
            if ok
            else (err or "Db2 unreachable")
        )
        return out

    async def get_vector_db_status(self, *, force_refresh: bool = False) -> Dict[str, Any]:
        """Cached status for the configured Db2 / vector backend (for APIs and UI)."""
        async with self._vector_db_probe_lock:
            now = time.monotonic()
            if (
                not force_refresh
                and self._vector_db_probe_cache is not None
                and (now - self._vector_db_probe_monotonic) < _VECTOR_DB_PROBE_TTL_SEC
            ):
                return dict(self._vector_db_probe_cache)
            try:
                result = await asyncio.to_thread(self._probe_vector_db_sync)
            except Exception as exc:
                result = {
                    "configured_type": (settings.vector_db_type or "unknown").lower(),
                    "kb_store_backend": self._backend,
                    "reachable": False,
                    "error": str(exc),
                    "detail": f"Vector DB probe failed: {exc}",
                }
            self._vector_db_probe_cache = result
            self._vector_db_probe_monotonic = now
            return dict(result)

    def invalidate_vector_db_probe_cache(self) -> None:
        """Drop cached probe so the next status call re-checks connectivity."""
        self._vector_db_probe_cache = None

    def get_backend_info(self) -> Dict[str, Any]:
        """Expose KB backend metadata for the UI / status endpoint."""
        rc = get_runtime_config()
        emb = embedding_runtime_summary(settings, rc)
        return {
            "backend": self._backend,
            "vector_db_type": settings.vector_db_type,
            "ollama_base_url": rc.ollama_base_url(),
            "embeddings": emb,
            "embedding_model": emb.get("model", ""),
            "embedding_provider": emb.get("provider", ""),
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
            finally:
                self.invalidate_vector_db_probe_cache()

        try:
            self._persist_sqlite(self._documents[document_id], chunk_records)
        except Exception as exc:
            logger.warning("SQLite KB persist failed: %s", exc)

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
            self.invalidate_vector_db_probe_cache()
        if existed:
            try:
                kb_sqlite_delete_document(self._sqlite_path, document_id)
            except Exception as exc:
                logger.warning("SQLite KB delete failed: %s", exc)
        return existed

    async def list_documents(self) -> List[Dict[str, Any]]:
        async with self._lock:
            return [self._serialize_document(d) for d in sorted(
                self._documents.values(),
                key=lambda d: d.created_at,
                reverse=True,
            )]

    async def get_document_detail(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Serialized document plus chunk text/metadata (no embedding vectors)."""
        async with self._lock:
            doc = self._documents.get(document_id)
            if doc is None:
                return None
            out = self._serialize_document(doc)
            chunks = self._chunks.get(document_id, [])
            out["chunks"] = [
                {
                    "id": ch.id,
                    "chunk_index": ch.chunk_index,
                    "content": ch.content,
                    "metadata": dict(ch.metadata),
                }
                for ch in sorted(chunks, key=lambda c: c.chunk_index)
            ]
            return out

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


def reset_knowledge_base_service() -> None:
    """Drop the singleton so the next access picks up new Db2 / env configuration."""
    global _knowledge_base_service
    _knowledge_base_service = None


def get_knowledge_base_service() -> KnowledgeBaseService:
    """Return the singleton knowledge base service."""
    global _knowledge_base_service
    if _knowledge_base_service is None:
        _knowledge_base_service = KnowledgeBaseService()
    return _knowledge_base_service


# Made with Bob
