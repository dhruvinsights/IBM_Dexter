"""Factory pattern for creating vector store instances."""

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


class VectorStoreFactory:
    """Factory for creating vector store instances based on configuration."""

    @staticmethod
    def create_vector_store(db_type: Optional[str] = None) -> VectorStoreProtocol:
        """Create a vector store instance based on the specified type.
        
        Args:
            db_type: Type of vector database to use. If None, uses config setting.
                    Options: inmemory, db2, qdrant, weaviate, chromadb
                    
        Returns:
            Vector store instance implementing VectorStoreProtocol
            
        Raises:
            ValueError: If the specified db_type is not supported
            ImportError: If required dependencies for the db_type are not installed
        """
        settings = get_settings()
        db_type = db_type or settings.vector_db_type
        
        logger.info(f"Creating vector store of type: {db_type}")
        
        if db_type == "inmemory":
            from app.rag.vector_store import InMemoryVectorStore
            return InMemoryVectorStore()
        
        elif db_type == "db2":
            try:
                from app.rag.db2_vector_store import Db2VectorStore
            except ImportError as e:
                raise ImportError(
                    "IBM Db2 dependencies not installed. "
                    "Install with: pip install ibm-db ibm-db-sa"
                ) from e
            
            return Db2VectorStore(
                database=settings.db2_database,
                hostname=settings.db2_hostname,
                port=settings.db2_port,
                protocol=settings.db2_protocol,
                uid=settings.db2_uid,
                pwd=settings.db2_pwd,
                schema=settings.db2_schema,
                table_name=settings.db2_table_name,
                embedding_dimension=settings.db2_embedding_dimension,
            )
        
        elif db_type == "qdrant":
            try:
                from qdrant_client import QdrantClient
                from qdrant_client.models import Distance, VectorParams
            except ImportError as e:
                raise ImportError(
                    "Qdrant dependencies not installed. "
                    "Install with: pip install qdrant-client"
                ) from e
            
            # Placeholder for Qdrant implementation
            raise NotImplementedError("Qdrant vector store not yet implemented")
        
        elif db_type == "weaviate":
            try:
                import weaviate
            except ImportError as e:
                raise ImportError(
                    "Weaviate dependencies not installed. "
                    "Install with: pip install weaviate-client"
                ) from e
            
            # Placeholder for Weaviate implementation
            raise NotImplementedError("Weaviate vector store not yet implemented")
        
        elif db_type == "chromadb":
            try:
                import chromadb
            except ImportError as e:
                raise ImportError(
                    "ChromaDB dependencies not installed. "
                    "Install with: pip install chromadb"
                ) from e
            
            # Placeholder for ChromaDB implementation
            raise NotImplementedError("ChromaDB vector store not yet implemented")
        
        else:
            raise ValueError(
                f"Unsupported vector database type: {db_type}. "
                f"Supported types: inmemory, db2, qdrant, weaviate, chromadb"
            )


def get_vector_store() -> VectorStoreProtocol:
    """Get the configured vector store instance.
    
    This is a convenience function that creates a vector store
    using the application's configuration settings.
    
    Returns:
        Vector store instance
    """
    return VectorStoreFactory.create_vector_store()


# Made with Bob