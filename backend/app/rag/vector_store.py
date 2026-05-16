"""Vector Store Service with Collection Management.

This module provides a unified interface for managing multiple vector store
collections for different document types in the RAG pipeline.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class InMemoryVectorStore:
    """Store vectors and metadata for semantic lookup."""

    def __init__(self) -> None:
        """Initialize the in-memory vector storage."""
        self._items: list[dict[str, Any]] = []

    async def add(self, document_id: str, content: str, embedding: list[float]) -> None:
        """Insert a document embedding into the store."""
        self._items.append(
            {
                "id": document_id,
                "content": content,
                "embedding": embedding,
            }
        )

    async def search(self, query_embedding: list[float], limit: int = 5) -> list[dict[str, Any]]:
        """Return the nearest stored items using dot-product similarity."""
        scored_items = []
        for item in self._items:
            score = sum(left * right for left, right in zip(query_embedding, item["embedding"]))
            scored_items.append({**item, "score": score})
        return sorted(scored_items, key=lambda item: item["score"], reverse=True)[:limit]


class VectorStoreService:
    """Manages multiple vector store collections for different document types.
    
    This service provides a unified interface for working with multiple collections
    (tables) in the vector database, each dedicated to a specific document type.
    
    Examples:
        - 'code_embeddings' for source code chunks
        - 'docs_embeddings' for documentation
        - 'pr_history' for historical PR reviews
        - 'architecture_docs' for architecture documents
        - 'security_policies' for security standards
    """

    def __init__(self, vector_store_type: str = "inmemory"):
        """Initialize the vector store service.
        
        Args:
            vector_store_type: Type of vector store ('inmemory', 'db2', etc.)
        """
        self.vector_store_type = vector_store_type
        self._collections: Dict[str, Any] = {}
        logger.info(f"VectorStoreService initialized with type: {vector_store_type}")

    async def get_collection(
        self,
        collection_name: str,
        create_if_missing: bool = True,
    ) -> Any:
        """Get or create a collection for specific document type.
        
        Args:
            collection_name: Name of the collection (e.g., 'code_embeddings', 'docs_embeddings')
            create_if_missing: Whether to create the collection if it doesn't exist
            
        Returns:
            Vector store instance for the collection
            
        Examples:
            >>> service = VectorStoreService(vector_store_type='db2')
            >>> code_store = await service.get_collection('code_embeddings')
            >>> docs_store = await service.get_collection('docs_embeddings')
        """
        if collection_name in self._collections:
            logger.debug(f"Returning existing collection: {collection_name}")
            return self._collections[collection_name]
        
        if not create_if_missing:
            logger.warning(f"Collection '{collection_name}' not found and create_if_missing=False")
            return None
        
        # Create new collection based on vector store type
        if self.vector_store_type == "inmemory":
            collection = InMemoryVectorStore()
            logger.info(f"Created in-memory collection: {collection_name}")
        elif self.vector_store_type == "db2":
            collection = await self._create_db2_collection(collection_name)
            logger.info(f"Created Db2 collection: {collection_name}")
        else:
            raise ValueError(f"Unsupported vector store type: {self.vector_store_type}")
        
        self._collections[collection_name] = collection
        return collection

    async def _create_db2_collection(self, collection_name: str) -> Any:
        """Create a Db2 vector store collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Db2VSIntegration instance for the collection
        """
        from app.core.config import get_settings
        from app.rag.db2vs_integration import Db2VSIntegration
        
        settings = get_settings()
        
        db2vs = Db2VSIntegration(
            database=settings.db2_database,
            hostname=settings.db2_hostname,
            port=settings.db2_port,
            protocol=settings.db2_protocol,
            uid=settings.db2_uid,
            pwd=settings.db2_pwd,
            schema=settings.db2_schema,
            collection_name=collection_name,
            table_prefix=getattr(settings, 'db2_table_prefix', 'DEXTER'),
            embedding_dimension=settings.embedding_dimension,
        )
        
        # Initialize the collection (db2vs will create table automatically)
        await db2vs.initialize()
        
        return db2vs

    async def list_collections(self) -> List[str]:
        """List all available collections.
        
        Returns:
            List of collection names
        """
        if self.vector_store_type == "inmemory":
            return list(self._collections.keys())
        elif self.vector_store_type == "db2":
            return await self._list_db2_collections()
        else:
            return list(self._collections.keys())

    async def _list_db2_collections(self) -> List[str]:
        """List all Db2 collections (tables) in the schema.
        
        Returns:
            List of collection names
        """
        from app.core.config import get_settings
        from app.rag.db2vs_integration import Db2VSIntegration
        
        settings = get_settings()
        
        # Create a temporary integration instance to query collections
        db2vs = Db2VSIntegration(
            database=settings.db2_database,
            hostname=settings.db2_hostname,
            port=settings.db2_port,
            protocol=settings.db2_protocol,
            uid=settings.db2_uid,
            pwd=settings.db2_pwd,
            schema=settings.db2_schema,
            collection_name="temp",  # Temporary, not used
            table_prefix=getattr(settings, 'db2_table_prefix', 'DEXTER'),
            embedding_dimension=settings.embedding_dimension,
        )
        
        return await db2vs.list_collections()

    async def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection.
        
        Args:
            collection_name: Name of the collection to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        if collection_name in self._collections:
            del self._collections[collection_name]
            logger.info(f"Deleted collection from cache: {collection_name}")
        
        if self.vector_store_type == "db2":
            # For Db2, we would need to drop the table
            # This is intentionally not implemented for safety
            logger.warning(f"Db2 collection deletion not implemented for safety: {collection_name}")
            return False
        
        return True

    def get_collection_info(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Dictionary with collection information or None if not found
        """
        if collection_name not in self._collections:
            return None
        
        collection = self._collections[collection_name]
        
        info = {
            "name": collection_name,
            "type": self.vector_store_type,
            "exists": True,
        }
        
        # Add type-specific information
        if hasattr(collection, 'get_connection_info'):
            info.update(collection.get_connection_info())
        
        return info


# Predefined collection names for RAG pipeline
class CollectionNames:
    """Standard collection names for IBM Dexter RAG pipeline."""
    
    CODE_EMBEDDINGS = "code_embeddings"
    DOCS_EMBEDDINGS = "docs_embeddings"
    PR_HISTORY = "pr_history"
    ARCHITECTURE_DOCS = "architecture_docs"
    SECURITY_POLICIES = "security_policies"
    COMPLIANCE_RULES = "compliance_rules"
    MODERNIZATION_GUIDES = "modernization_guides"
    TEST_PATTERNS = "test_patterns"
    API_DOCUMENTATION = "api_documentation"
    
    @classmethod
    def all(cls) -> List[str]:
        """Get all predefined collection names.
        
        Returns:
            List of all collection names
        """
        return [
            cls.CODE_EMBEDDINGS,
            cls.DOCS_EMBEDDINGS,
            cls.PR_HISTORY,
            cls.ARCHITECTURE_DOCS,
            cls.SECURITY_POLICIES,
            cls.COMPLIANCE_RULES,
            cls.MODERNIZATION_GUIDES,
            cls.TEST_PATTERNS,
            cls.API_DOCUMENTATION,
        ]


# Made with Bob
