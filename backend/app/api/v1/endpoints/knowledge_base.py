"""Knowledge base API endpoints (upload, list, search, delete)."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, Form, HTTPException, Response, UploadFile, status
from pydantic import BaseModel, Field

from app.services.document_extract import extract_text_from_bytes
from app.services.knowledge_base_service import get_knowledge_base_service

logger = logging.getLogger(__name__)
router = APIRouter()


# --------------------------------------------------------------------------- #
# Schemas
# --------------------------------------------------------------------------- #


class IngestTextRequest(BaseModel):
    """Inline text ingestion payload."""

    title: str = Field(..., min_length=1, max_length=256)
    content: str = Field(..., min_length=1)
    source: str = "manual"
    content_type: str = "text/plain"
    tags: List[str] = Field(default_factory=list)


class SearchRequest(BaseModel):
    """RAG search payload."""

    query: str = Field(..., min_length=1)
    limit: int = Field(default=4, ge=1, le=20)


class DocumentResponse(BaseModel):
    """Document summary returned to the UI."""

    id: str
    title: str
    source: str
    content_type: str
    chunk_count: int
    size_bytes: int
    created_at: str
    tags: List[str]


class DocumentChunkResponse(BaseModel):
    """One chunk of ingested text (embedding vectors are omitted)."""

    id: str
    chunk_index: int
    content: str
    metadata: Dict[str, Any]


class DocumentDetailResponse(DocumentResponse):
    """Full document with chunk bodies for review in the UI."""

    chunks: List[DocumentChunkResponse]


# --------------------------------------------------------------------------- #
# Endpoints
# --------------------------------------------------------------------------- #


@router.get("/knowledge-base/status")
async def kb_status() -> Dict[str, Any]:
    """Backend / model status for the Knowledge Base page."""
    service = get_knowledge_base_service()
    healthy = await service.embeddings.health()
    docs = await service.list_documents()
    total_chunks = sum(d["chunk_count"] for d in docs)
    vdb = await service.get_vector_db_status()
    return {
        **service.get_backend_info(),
        "vector_db_reachable": vdb.get("reachable"),
        "vector_db_error": vdb.get("error"),
        "vector_db_detail": vdb.get("detail"),
        "vector_db_status": vdb,
        "embeddings_healthy": healthy,
        "document_count": len(docs),
        "chunk_count": total_chunks,
    }


@router.get("/knowledge-base/documents", response_model=List[DocumentResponse])
async def list_documents() -> List[DocumentResponse]:
    service = get_knowledge_base_service()
    docs = await service.list_documents()
    return [DocumentResponse(**d) for d in docs]


@router.get("/knowledge-base/documents/{document_id}", response_model=DocumentDetailResponse)
async def get_document(document_id: str) -> DocumentDetailResponse:
    """Return document metadata and all chunks (full text)."""
    service = get_knowledge_base_service()
    detail = await service.get_document_detail(document_id)
    if detail is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return DocumentDetailResponse(**detail)


@router.post(
    "/knowledge-base/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def ingest_text(payload: IngestTextRequest) -> DocumentResponse:
    service = get_knowledge_base_service()
    try:
        doc = await service.ingest(
            title=payload.title,
            content=payload.content,
            source=payload.source,
            content_type=payload.content_type,
            tags=payload.tags,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        logger.exception("Knowledge base ingest failed")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    return DocumentResponse(**doc)


@router.post(
    "/knowledge-base/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(default=None),
    tags: Optional[str] = Form(default=None),
) -> DocumentResponse:
    """Upload a document to the knowledge base (UTF-8 text, markdown, PDF, DOCX, code)."""
    raw = await file.read()
    filename = file.filename or "document"
    try:
        content, ctype = extract_text_from_bytes(filename, raw, file.content_type)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    service = get_knowledge_base_service()
    parsed_tags = [t.strip() for t in (tags or "").split(",") if t.strip()]
    try:
        doc = await service.ingest(
            title=title or file.filename or "document",
            content=content,
            source=f"upload:{filename}",
            content_type=ctype,
            tags=parsed_tags,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        logger.exception("Knowledge base upload failed")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    return DocumentResponse(**doc)


@router.delete(
    "/knowledge-base/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_document(document_id: str) -> Response:
    service = get_knowledge_base_service()
    deleted = await service.delete(document_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/knowledge-base/search")
async def search_documents(payload: SearchRequest) -> Dict[str, Any]:
    service = get_knowledge_base_service()
    results = await service.search(payload.query, limit=payload.limit)
    return {"query": payload.query, "results": results}


# Made with Bob
