"""SQLite persistence for in-memory knowledge base (survives backend restarts)."""

from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path
from typing import Any, Dict, List, Tuple

_lock = threading.Lock()


def _connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS kb_documents (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            source TEXT NOT NULL,
            content_type TEXT NOT NULL,
            chunk_count INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            size_bytes INTEGER NOT NULL,
            tags_json TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS kb_chunks (
            id TEXT PRIMARY KEY,
            document_id TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            content TEXT NOT NULL,
            embedding_json TEXT NOT NULL,
            metadata_json TEXT NOT NULL,
            FOREIGN KEY(document_id) REFERENCES kb_documents(id) ON DELETE CASCADE
        );
        """
    )
    conn.commit()


def load_all(path: Path) -> Tuple[List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]:
    """Return (serialized_document_dicts, embedding_chunk_payloads_by_document_id).

    Chunk payloads match KnowledgeBaseService internal shape: id, document_id,
    chunk_index, content, embedding, metadata.
    """
    if not path.exists():
        return [], {}
    conn = _connect(path)
    try:
        init_schema(conn)
        documents: List[Dict[str, Any]] = []
        for row in conn.execute("SELECT * FROM kb_documents ORDER BY created_at"):
            d = dict(row)
            d["tags"] = json.loads(d.pop("tags_json") or "[]")
            documents.append(d)

        chunks_map: Dict[str, List[Dict[str, Any]]] = {}
        for row in conn.execute("SELECT * FROM kb_chunks ORDER BY document_id, chunk_index"):
            c = {
                "id": row["id"],
                "document_id": row["document_id"],
                "chunk_index": row["chunk_index"],
                "content": row["content"],
                "embedding": json.loads(row["embedding_json"]),
                "metadata": json.loads(row["metadata_json"]),
            }
            chunks_map.setdefault(c["document_id"], []).append(c)
        return documents, chunks_map
    finally:
        conn.close()


def replace_document(
    path: Path,
    doc: Dict[str, Any],
    chunks: List[Dict[str, Any]],
) -> None:
    """Upsert one document and its chunks (replace by id)."""
    with _lock:
        conn = _connect(path)
        try:
            init_schema(conn)
            conn.execute("DELETE FROM kb_chunks WHERE document_id = ?", (doc["id"],))
            conn.execute("DELETE FROM kb_documents WHERE id = ?", (doc["id"],))
            conn.execute(
                """
                INSERT INTO kb_documents
                (id, title, source, content_type, chunk_count, created_at, size_bytes, tags_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    doc["id"],
                    doc["title"],
                    doc["source"],
                    doc["content_type"],
                    doc["chunk_count"],
                    doc["created_at"],
                    doc["size_bytes"],
                    json.dumps(doc.get("tags") or []),
                ),
            )
            for ch in chunks:
                conn.execute(
                    """
                    INSERT INTO kb_chunks
                    (id, document_id, chunk_index, content, embedding_json, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        ch["id"],
                        ch["document_id"],
                        ch["chunk_index"],
                        ch["content"],
                        json.dumps(ch["embedding"]),
                        json.dumps(ch["metadata"]),
                    ),
                )
            conn.commit()
        finally:
            conn.close()


def delete_document(path: Path, document_id: str) -> None:
    with _lock:
        conn = _connect(path)
        try:
            init_schema(conn)
            conn.execute("DELETE FROM kb_chunks WHERE document_id = ?", (document_id,))
            conn.execute("DELETE FROM kb_documents WHERE id = ?", (document_id,))
            conn.commit()
        finally:
            conn.close()
