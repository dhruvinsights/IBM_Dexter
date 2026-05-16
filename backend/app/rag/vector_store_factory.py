"""Factory pattern for creating vector store instances.

IBM Dexter uses IBM Db2 as the production vector store via the official
`langchain-db2` integration. An in-memory store is provided for tests and
local development without a Db2 instance.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Protocol

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class VectorStoreProtocol(Protocol):
    """Protocol defining the interface for vector stores."""

    async def initialize(self) -> None:
        """Initialize the vector store."""
        ...

    async def add(
        self,
        document_id: str,
        content: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a document to the vector store."""
        ...

    async def search(
        self,
        query_embedding: List[float],
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        ...

    async def delete(self, document_id: str) -> bool:
        """Delete a document from the vector store."""
        ...

    async def clear(self) -> None:
        """Clear all documents from the vector store."""
        ...

    async def count(self) -> int:
        """Get the total number of documents."""
        ...


SUPPORTED_VECTOR_DBS = ("inmemory", "db2")


class VectorStoreFactory:
    """Factory for creating vector store instances based on configuration."""

    @staticmethod
    def create_vector_store(db_type: Optional[str] = None) -> VectorStoreProtocol:
        """Create a vector store instance based on the specified type.

        Args:
            db_type: Type of vector database to use. If None, uses config setting.
                    Supported options: inmemory, db2.

        Returns:
            Vector store instance implementing VectorStoreProtocol

        Raises:
            ValueError: If the specified db_type is not supported.
            ImportError: If required dependencies for the db_type are not installed.
        """
        settings = get_settings()
        db_type = (db_type or settings.vector_db_type or "inmemory").lower()

        logger.info("Creating vector store of type: %s", db_type)

        if db_type == "inmemory":
            from app.rag.vector_store import InMemoryVectorStore
            return InMemoryVectorStore()

        if db_type == "db2":
            try:
                from app.rag.db2_vector_store import Db2VectorStore
            except ImportError as exc:
                raise ImportError(
                    "IBM Db2 dependencies not installed. "
                    "Install with: pip install langchain-db2 ibm-db ibm-db-sa"
                ) from exc

            return Db2VectorStore(
                database=settings.db2_database,
                hostname=settings.db2_hostname,
                port=settings.db2_port,
                protocol=settings.db2_protocol,
                uid=settings.db2_uid,
                pwd=settings.db2_pwd,
                schema=settings.db2_schema,
                table_name=settings.db2_table_prefix,
                embedding_dimension=settings.embedding_dimension,
            )

        raise ValueError(
            f"Unsupported vector database type: {db_type}. "
            f"Supported types: {', '.join(SUPPORTED_VECTOR_DBS)}"
        )


def get_vector_store() -> VectorStoreProtocol:
    """Get the configured vector store instance.

    This is a convenience function that creates a vector store
    using the application's configuration settings.

    Returns:
        Vector store instance.
    """
    return VectorStoreFactory.create_vector_store()


# Made with Bob
