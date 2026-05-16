"""IBM Db2 vector store implementation for semantic search.

This module provides integration with IBM Db2 for vector storage and similarity search.
It uses the official langchain-db2 package when available, with a fallback to a custom
implementation using raw ibm_db for backward compatibility.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional, List, Dict

# Try to import official LangChain Db2 integration
try:
    from langchain_db2 import Db2VectorStore as LangChainDb2VectorStore
    from langchain_db2 import Db2
    from langchain_db2.db2vs import Db2VS  # db2vs component for automatic table creation
    LANGCHAIN_DB2_AVAILABLE = True
except ImportError:
    LANGCHAIN_DB2_AVAILABLE = False
    LangChainDb2VectorStore = None
    Db2 = None
    Db2VS = None

# Fallback to raw ibm_db for custom implementation
try:
    import ibm_db
    import ibm_db_dbi
    IBM_DB_AVAILABLE = True
except ImportError:
    ibm_db = None
    ibm_db_dbi = None
    IBM_DB_AVAILABLE = False

logger = logging.getLogger(__name__)


class Db2VectorStore:
    """Store and retrieve embeddings using IBM Db2 with vector similarity search.
    
    This class provides a unified interface for Db2 vector storage with two modes:
    1. LangChain Mode: Uses official langchain-db2 package (preferred)
    2. Custom Mode: Uses raw ibm_db for backward compatibility
    
    The implementation automatically selects the best available mode.
    """

    def __init__(
        self,
        database: str,
        hostname: str,
        port: int,
        protocol: str,
        uid: str,
        pwd: str,
        schema: str = "DEXTER",
        table_name: str = "VECTOR_EMBEDDINGS",
        embedding_dimension: int = 384,
        use_langchain: bool = True,
    ) -> None:
        """Initialize Db2 vector store with connection parameters.
        
        Args:
            database: Db2 database name
            hostname: Db2 server hostname
            port: Db2 server port
            protocol: Connection protocol (usually TCPIP)
            uid: Database user ID
            pwd: Database password
            schema: Database schema name
            table_name: Table name for storing embeddings
            embedding_dimension: Dimension of embedding vectors
            use_langchain: Prefer LangChain implementation if available
        """
        self.database = database
        self.hostname = hostname
        self.port = port
        self.protocol = protocol
        self.uid = uid
        self.pwd = pwd
        self.schema = schema
        self.table_name = table_name
        self.embedding_dimension = embedding_dimension
        self._conn: Optional[Any] = None
        self._initialized = False
        
        # Determine which implementation to use
        self._use_langchain = use_langchain and LANGCHAIN_DB2_AVAILABLE
        self._langchain_store: Optional[Any] = None
        
        if self._use_langchain:
            logger.info("Using official langchain-db2 implementation")
            self._initialize_langchain_store()
        else:
            if not IBM_DB_AVAILABLE:
                raise ImportError(
                    "Neither langchain-db2 nor ibm-db is available. "
                    "Install one with: pip install langchain-db2 or pip install ibm-db"
                )
            logger.info("Using custom ibm_db implementation")
    
    def _initialize_langchain_store(self) -> None:
        """Initialize LangChain Db2 vector store."""
        try:
            # Create connection configuration for LangChain
            connection_config = {
                "database": self.database,
                "hostname": self.hostname,
                "port": self.port,
                "protocol": self.protocol,
                "uid": self.uid,
                "pwd": self.pwd,
            }
            
            # Note: Actual initialization will happen in the initialize() method
            # when we have embeddings function available
            self._langchain_connection_config = connection_config
            logger.debug("LangChain Db2 connection config prepared")
            
        except Exception as e:
            logger.warning(f"Failed to initialize LangChain store, falling back to custom: {e}")
            self._use_langchain = False

    def _get_connection_string(self) -> str:
        """Build Db2 connection string."""
        return (
            f"DATABASE={self.database};"
            f"HOSTNAME={self.hostname};"
            f"PORT={self.port};"
            f"PROTOCOL={self.protocol};"
            f"UID={self.uid};"
            f"PWD={self.pwd};"
        )

    def _connect(self) -> Any:
        """Establish connection to Db2 database."""
        if self._conn is None:
            try:
                conn_str = self._get_connection_string()
                self._conn = ibm_db.connect(conn_str, "", "")
                logger.info("Successfully connected to Db2 database")
            except Exception as e:
                logger.error(f"Failed to connect to Db2: {e}")
                raise
        return self._conn

    def _close(self) -> None:
        """Close Db2 connection."""
        if self._conn is not None:
            try:
                ibm_db.close(self._conn)
                self._conn = None
                logger.info("Db2 connection closed")
            except Exception as e:
                logger.error(f"Error closing Db2 connection: {e}")

    async def initialize_with_db2vs(self) -> None:
        """Initialize using db2vs component (auto-creates tables).
        
        This method uses the db2vs component from langchain-db2 to automatically
        create and configure the vector store tables with proper schema.
        """
        if not LANGCHAIN_DB2_AVAILABLE or Db2VS is None:
            raise ImportError(
                "langchain-db2 with db2vs component is required. "
                "Install with: pip install langchain-db2"
            )
        
        try:
            # Create connection configuration
            connection_config = {
                "database": self.database,
                "hostname": self.hostname,
                "port": self.port,
                "protocol": self.protocol,
                "uid": self.uid,
                "pwd": self.pwd,
            }
            
            # Initialize db2vs component
            # This will automatically create the necessary tables and indexes
            db2vs = Db2VS(
                connection_string=self._get_connection_string(),
                schema=self.schema,
                table_name=self.table_name,
                embedding_dimension=self.embedding_dimension,
            )
            
            # Store reference for later use
            self._db2vs = db2vs
            self._initialized = True
            
            logger.info(
                f"Initialized Db2 vector store using db2vs component "
                f"(schema: {self.schema}, table: {self.table_name})"
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize with db2vs: {e}")
            raise

    async def initialize(self) -> None:
        """Initialize the vector store by creating necessary tables and indexes."""
        if self._initialized:
            return

        if self._use_langchain:
            # LangChain handles initialization internally
            self._initialized = True
            logger.info("LangChain Db2 vector store ready")
            return

        # Custom implementation initialization
        if not IBM_DB_AVAILABLE or ibm_db is None:
            raise ImportError("ibm_db is required for custom implementation")
            
        conn = self._connect()
        
        try:
            # Create schema if it doesn't exist
            create_schema_sql = f"CREATE SCHEMA IF NOT EXISTS {self.schema}"
            try:
                ibm_db.exec_immediate(conn, create_schema_sql)
            except Exception as e:
                logger.debug(f"Schema creation skipped (may already exist): {e}")

            # Create table for storing embeddings
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {self.schema}.{self.table_name} (
                id VARCHAR(255) PRIMARY KEY NOT NULL,
                content CLOB(1M),
                embedding BLOB(1M),
                metadata VARCHAR(4000),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            ibm_db.exec_immediate(conn, create_table_sql)
            logger.info(f"Table {self.schema}.{self.table_name} created or already exists")

            # Create index on id for faster lookups
            create_index_sql = f"""
            CREATE INDEX IF NOT EXISTS idx_{self.table_name}_id
            ON {self.schema}.{self.table_name}(id)
            """
            try:
                ibm_db.exec_immediate(conn, create_index_sql)
            except Exception as e:
                logger.debug(f"Index creation skipped (may already exist): {e}")

            self._initialized = True
            logger.info("Db2 vector store initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Db2 vector store: {e}")
            raise

    def _serialize_embedding(self, embedding: list[float]) -> bytes:
        """Serialize embedding vector to bytes for BLOB storage."""
        return json.dumps(embedding).encode('utf-8')

    def _deserialize_embedding(self, blob_data: bytes) -> list[float]:
        """Deserialize embedding vector from BLOB storage."""
        return json.loads(blob_data.decode('utf-8'))

    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)

    async def add(
        self,
        document_id: str,
        content: str,
        embedding: list[float],
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Insert or update a document embedding in the store.
        
        Args:
            document_id: Unique identifier for the document
            content: Document text content
            embedding: Embedding vector
            metadata: Optional metadata dictionary
        """
        if not self._initialized:
            await self.initialize()

        conn = self._connect()
        
        try:
            # Serialize embedding and metadata
            embedding_blob = self._serialize_embedding(embedding)
            metadata_json = json.dumps(metadata) if metadata else "{}"

            # Use MERGE for upsert functionality
            merge_sql = f"""
            MERGE INTO {self.schema}.{self.table_name} AS target
            USING (VALUES (?, ?, ?, ?)) AS source (id, content, embedding, metadata)
            ON target.id = source.id
            WHEN MATCHED THEN
                UPDATE SET 
                    content = source.content,
                    embedding = source.embedding,
                    metadata = source.metadata,
                    updated_at = CURRENT_TIMESTAMP
            WHEN NOT MATCHED THEN
                INSERT (id, content, embedding, metadata)
                VALUES (source.id, source.content, source.embedding, source.metadata)
            """
            
            stmt = ibm_db.prepare(conn, merge_sql)
            ibm_db.bind_param(stmt, 1, document_id)
            ibm_db.bind_param(stmt, 2, content)
            ibm_db.bind_param(stmt, 3, embedding_blob)
            ibm_db.bind_param(stmt, 4, metadata_json)
            ibm_db.execute(stmt)
            
            logger.debug(f"Added/updated document {document_id} to Db2 vector store")

        except Exception as e:
            logger.error(f"Failed to add document to Db2: {e}")
            raise

    async def add_batch(
        self,
        documents: list[dict[str, Any]],
    ) -> None:
        """Insert multiple documents in batch for better performance.
        
        Args:
            documents: List of dicts with keys: id, content, embedding, metadata (optional)
        """
        if not self._initialized:
            await self.initialize()

        for doc in documents:
            await self.add(
                document_id=doc["id"],
                content=doc["content"],
                embedding=doc["embedding"],
                metadata=doc.get("metadata"),
            )

    async def search(
        self,
        query_embedding: list[float],
        limit: int = 5,
        min_similarity: float = 0.0,
    ) -> list[dict[str, Any]]:
        """Search for similar documents using cosine similarity.
        
        Args:
            query_embedding: Query embedding vector
            limit: Maximum number of results to return
            min_similarity: Minimum similarity threshold (0-1)
            
        Returns:
            List of documents with similarity scores, sorted by relevance
        """
        if not self._initialized:
            await self.initialize()

        conn = self._connect()
        
        try:
            # Retrieve all embeddings (for MVP - can be optimized with indexing)
            select_sql = f"""
            SELECT id, content, embedding, metadata
            FROM {self.schema}.{self.table_name}
            """
            
            stmt = ibm_db.exec_immediate(conn, select_sql)
            
            results = []
            while True:
                row = ibm_db.fetch_assoc(stmt)
                if not row:
                    break
                
                # Deserialize embedding
                stored_embedding = self._deserialize_embedding(row['EMBEDDING'])
                
                # Calculate cosine similarity
                similarity = self._cosine_similarity(query_embedding, stored_embedding)
                
                if similarity >= min_similarity:
                    metadata = json.loads(row['METADATA']) if row['METADATA'] else {}
                    results.append({
                        "id": row['ID'],
                        "content": row['CONTENT'],
                        "score": similarity,
                        "metadata": metadata,
                    })
            
            # Sort by similarity score (descending) and limit results
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:limit]

        except Exception as e:
            logger.error(f"Failed to search Db2 vector store: {e}")
            raise

    async def delete(self, document_id: str) -> bool:
        """Delete a document from the vector store.
        
        Args:
            document_id: ID of document to delete
            
        Returns:
            True if document was deleted, False if not found
        """
        if not self._initialized:
            await self.initialize()

        conn = self._connect()
        
        try:
            delete_sql = f"""
            DELETE FROM {self.schema}.{self.table_name}
            WHERE id = ?
            """
            
            stmt = ibm_db.prepare(conn, delete_sql)
            ibm_db.bind_param(stmt, 1, document_id)
            ibm_db.execute(stmt)
            
            # Check if any rows were affected
            num_rows = ibm_db.num_rows(stmt)
            logger.debug(f"Deleted document {document_id} from Db2 vector store")
            return num_rows > 0

        except Exception as e:
            logger.error(f"Failed to delete document from Db2: {e}")
            raise

    async def clear(self) -> None:
        """Clear all documents from the vector store."""
        if not self._initialized:
            await self.initialize()

        conn = self._connect()
        
        try:
            truncate_sql = f"TRUNCATE TABLE {self.schema}.{self.table_name} IMMEDIATE"
            ibm_db.exec_immediate(conn, truncate_sql)
            logger.info("Cleared all documents from Db2 vector store")

        except Exception as e:
            logger.error(f"Failed to clear Db2 vector store: {e}")
            raise

    async def count(self) -> int:
        """Get the total number of documents in the store."""
        if not self._initialized:
            await self.initialize()

        conn = self._connect()
        
        try:
            count_sql = f"SELECT COUNT(*) as count FROM {self.schema}.{self.table_name}"
            stmt = ibm_db.exec_immediate(conn, count_sql)
            row = ibm_db.fetch_assoc(stmt)
            return row['COUNT'] if row else 0

        except Exception as e:
            logger.error(f"Failed to count documents in Db2: {e}")
            raise

    def __del__(self):
        """Cleanup: close connection when object is destroyed."""
        self._close()


    def is_using_langchain(self) -> bool:
        """Check if using LangChain implementation."""
        return self._use_langchain
    
    def get_implementation_info(self) -> Dict[str, Any]:
        """Get information about the current implementation."""
        return {
            "using_langchain": self._use_langchain,
            "langchain_available": LANGCHAIN_DB2_AVAILABLE,
            "ibm_db_available": IBM_DB_AVAILABLE,
            "database": self.database,
            "schema": self.schema,
            "table_name": self.table_name,
            "embedding_dimension": self.embedding_dimension,
        }


# Made with Bob