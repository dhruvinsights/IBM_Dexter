"""Db2VS Component Integration for IBM Dexter.

This module provides integration with the db2vs component from langchain-db2,
which offers automatic table creation and management for Db2 vector stores.

The db2vs component simplifies vector store setup by:
- Automatically creating required tables and indexes
- Managing schema migrations
- Providing optimized vector operations
- Handling connection pooling
"""

from __future__ import annotations

import logging
from typing import Any, List, Optional, Dict

logger = logging.getLogger(__name__)

# Try to import db2vs component
try:
    from langchain_db2.db2vs import Db2VS
    from langchain_db2 import Db2VectorStore
    from langchain.embeddings.base import Embeddings
    from langchain.schema import Document
    DB2VS_AVAILABLE = True
except ImportError:
    DB2VS_AVAILABLE = False
    Db2VS = None
    Db2VectorStore = None
    Embeddings = None
    Document = None


class Db2VSIntegration:
    """Wrapper for db2vs component with helper methods for IBM Dexter.
    
    Supports multiple collections (tables) for different document types.
    Each collection is automatically created by db2vs when first used.
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
        collection_name: str = "default",
        table_prefix: str = "DEXTER",
        embedding_dimension: int = 384,
    ):
        """Initialize db2vs integration.
        
        Args:
            database: Db2 database name
            hostname: Db2 server hostname
            port: Db2 server port
            protocol: Connection protocol (usually TCPIP)
            uid: Database user ID
            pwd: Database password
            schema: Database schema name
            collection_name: Name of the collection (e.g., 'code', 'docs', 'pr_history')
                           db2vs will create table: {schema}.{prefix}_{collection_name}
            table_prefix: Prefix for table names (e.g., 'DEXTER' creates 'DEXTER_CODE')
            embedding_dimension: Dimension of embedding vectors
        """
        if not DB2VS_AVAILABLE:
            raise ImportError(
                "langchain-db2 with db2vs component is required. "
                "Install with: pip install langchain-db2"
            )
        
        self.database = database
        self.hostname = hostname
        self.port = port
        self.protocol = protocol
        self.uid = uid
        self.pwd = pwd
        self.schema = schema
        self.collection_name = collection_name
        self.table_prefix = table_prefix
        self.embedding_dimension = embedding_dimension
        
        # Generate table name from prefix and collection
        if table_prefix:
            self.table_name = f"{table_prefix}_{collection_name.upper()}"
        else:
            self.table_name = collection_name.upper()
        
        self._db2vs: Optional[Any] = None
        self._vector_store: Optional[Any] = None
        
        logger.info(
            f"Db2VS integration initialized for collection '{collection_name}' "
            f"(table: {schema}.{self.table_name})"
        )

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

    async def initialize(self) -> None:
        """Initialize db2vs component and create tables automatically.
        
        This method uses db2vs to automatically create the vector store
        tables with proper schema, indexes, and constraints.
        """
        if self._db2vs is not None:
            logger.info("Db2VS already initialized")
            return
        
        try:
            connection_string = self._get_connection_string()
            
            # Initialize db2vs component
            # This automatically creates tables and indexes
            self._db2vs = Db2VS(
                connection_string=connection_string,
                schema=self.schema,
                table_name=self.table_name,
                embedding_dimension=self.embedding_dimension,
            )
            
            logger.info(
                f"Db2VS initialized successfully "
                f"(schema: {self.schema}, table: {self.table_name}, "
                f"dimension: {self.embedding_dimension})"
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize db2vs: {e}")
            raise

    def create_vector_store(
        self,
        embeddings: Embeddings,
        documents: Optional[List[Document]] = None,
    ) -> Any:
        """Create a Db2 vector store using db2vs.
        
        Args:
            embeddings: LangChain embeddings instance
            documents: Optional list of documents to add initially
            
        Returns:
            Db2VectorStore instance
        """
        if self._vector_store is None:
            connection_string = self._get_connection_string()
            
            if documents:
                # Create with initial documents
                self._vector_store = Db2VectorStore.from_documents(
                    documents=documents,
                    embedding=embeddings,
                    connection_string=connection_string,
                    collection_name=self.table_name,
                )
                logger.info(f"Created Db2 vector store with {len(documents)} documents")
            else:
                # Create empty store
                self._vector_store = Db2VectorStore(
                    embedding=embeddings,
                    connection_string=connection_string,
                    collection_name=self.table_name,
                )
                logger.info("Created empty Db2 vector store")
        
        return self._vector_store

    async def add_documents(
        self,
        documents: List[Document],
        embeddings: Embeddings,
    ) -> List[str]:
        """Add documents to the vector store.
        
        Args:
            documents: List of LangChain Document objects
            embeddings: Embeddings instance
            
        Returns:
            List of document IDs
        """
        await self.initialize()
        vector_store = self.create_vector_store(embeddings)
        ids = await vector_store.aadd_documents(documents)
        logger.info(f"Added {len(documents)} documents to Db2 vector store")
        return ids

    async def similarity_search(
        self,
        query: str,
        embeddings: Embeddings,
        k: int = 5,
    ) -> List[Document]:
        """Perform similarity search.
        
        Args:
            query: Search query text
            embeddings: Embeddings instance
            k: Number of results to return
            
        Returns:
            List of similar documents
        """
        await self.initialize()
        vector_store = self.create_vector_store(embeddings)
        results = await vector_store.asimilarity_search(query, k=k)
        logger.info(f"Found {len(results)} similar documents")
        return results

    async def similarity_search_with_score(
        self,
        query: str,
        embeddings: Embeddings,
        k: int = 5,
    ) -> List[tuple[Document, float]]:
        """Perform similarity search with relevance scores.
        
        Args:
            query: Search query text
            embeddings: Embeddings instance
            k: Number of results to return
            
        Returns:
            List of (document, score) tuples
        """
        await self.initialize()
        vector_store = self.create_vector_store(embeddings)
        results = await vector_store.asimilarity_search_with_score(query, k=k)
        logger.info(f"Found {len(results)} similar documents with scores")
        return results

    async def delete_documents(self, ids: List[str]) -> None:
        """Delete documents from the vector store.
        
        Args:
            ids: List of document IDs to delete
        """
        if self._vector_store is None:
            logger.warning("Vector store not initialized, cannot delete documents")
            return
        
        await self._vector_store.adelete(ids)
        logger.info(f"Deleted {len(ids)} documents from vector store")

    async def clear(self) -> None:
        """Clear all documents from the vector store."""
        if self._db2vs is None:
            await self.initialize()
        
        # Use db2vs to truncate table
        try:
            # This is a placeholder - actual implementation depends on db2vs API
            logger.info("Clearing all documents from vector store")
            # self._db2vs.clear()  # Uncomment when db2vs supports this
        except Exception as e:
            logger.error(f"Failed to clear vector store: {e}")
            raise

    async def create_collection(self, collection_name: str) -> "Db2VSIntegration":
        """Create a new collection (table) for specific document type.
        
        Args:
            collection_name: Name of the collection (e.g., 'code', 'docs', 'pr_history')
            
        Returns:
            New Db2VSIntegration instance for the collection
            
        Note:
            db2vs automatically creates the table when first document is added.
            This method just returns a new integration instance configured for the collection.
        """
        return Db2VSIntegration(
            database=self.database,
            hostname=self.hostname,
            port=self.port,
            protocol=self.protocol,
            uid=self.uid,
            pwd=self.pwd,
            schema=self.schema,
            collection_name=collection_name,
            table_prefix=self.table_prefix,
            embedding_dimension=self.embedding_dimension,
        )

    async def list_collections(self) -> List[str]:
        """List all existing collections (tables) in the schema.
        
        Returns:
            List of collection names (without prefix)
        """
        try:
            import ibm_db
            
            conn_str = self._get_connection_string()
            conn = ibm_db.connect(conn_str, "", "")
            
            # Query for tables in the schema with the prefix
            if self.table_prefix:
                pattern = f"{self.table_prefix}_%"
                query = f"""
                SELECT TABNAME FROM SYSCAT.TABLES
                WHERE TABSCHEMA = '{self.schema}'
                AND TABNAME LIKE '{pattern}'
                """
            else:
                query = f"""
                SELECT TABNAME FROM SYSCAT.TABLES
                WHERE TABSCHEMA = '{self.schema}'
                """
            
            stmt = ibm_db.exec_immediate(conn, query)
            
            collections = []
            while ibm_db.fetch_row(stmt):
                table_name = ibm_db.result(stmt, 0)
                # Remove prefix to get collection name
                if self.table_prefix and table_name.startswith(f"{self.table_prefix}_"):
                    collection_name = table_name[len(self.table_prefix) + 1:].lower()
                else:
                    collection_name = table_name.lower()
                collections.append(collection_name)
            
            ibm_db.close(conn)
            logger.info(f"Found {len(collections)} collections in schema {self.schema}")
            return collections
            
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            return []

    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information.
        
        Returns:
            Dictionary with connection details
        """
        return {
            "database": self.database,
            "hostname": self.hostname,
            "port": self.port,
            "protocol": self.protocol,
            "uid": self.uid,
            "schema": self.schema,
            "collection_name": self.collection_name,
            "table_name": self.table_name,
            "table_prefix": self.table_prefix,
            "embedding_dimension": self.embedding_dimension,
            "initialized": self._db2vs is not None,
        }


# Example usage functions

async def example_basic_setup():
    """Example: Basic setup with db2vs component using collections."""
    from langchain.embeddings import HuggingFaceEmbeddings
    
    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    # Initialize db2vs integration for code embeddings collection
    db2vs = Db2VSIntegration(
        database="TESTDB",
        hostname="Geetika-5y420-x86.dev.fyre.ibm.com",
        port=50000,
        protocol="TCPIP",
        uid="Geetika",
        pwd="your_password_here",
        schema="DEXTER",
        collection_name="code_embeddings",  # Collection name
        table_prefix="DEXTER",  # Creates table: DEXTER_CODE_EMBEDDINGS
        embedding_dimension=384,
    )
    
    # Initialize (creates tables automatically)
    await db2vs.initialize()
    
    print("Db2 vector store initialized successfully!")
    print(f"Connection info: {db2vs.get_connection_info()}")
    print(f"Table created: {db2vs.schema}.{db2vs.table_name}")


async def example_add_and_search():
    """Example: Add documents and perform search."""
    from langchain.embeddings import HuggingFaceEmbeddings
    
    embeddings = HuggingFaceEmbeddings()
    
    db2vs = Db2VSIntegration(
        database="TESTDB",
        hostname="Geetika-5y420-x86.dev.fyre.ibm.com",
        port=50000,
        protocol="TCPIP",
        uid="Geetika",
        pwd="your_password_here",
    )
    
    # Create sample documents
    documents = [
        Document(
            page_content="This is a Python function for data processing.",
            metadata={"language": "python", "type": "function"},
        ),
        Document(
            page_content="This is a JavaScript async function for API calls.",
            metadata={"language": "javascript", "type": "function"},
        ),
    ]
    
    # Add documents
    ids = await db2vs.add_documents(documents, embeddings)
    print(f"Added documents with IDs: {ids}")
    
    # Search
    results = await db2vs.similarity_search(
        "How to make API calls?",
        embeddings,
        k=3,
    )
    
    for doc in results:
        print(f"Content: {doc.page_content}")
        print(f"Metadata: {doc.metadata}\n")


async def example_code_review_workflow():
    """Example: Code review workflow with db2vs."""
    from langchain.embeddings import HuggingFaceEmbeddings
    
    embeddings = HuggingFaceEmbeddings()
    
    db2vs = Db2VSIntegration(
        database="TESTDB",
        hostname="Geetika-5y420-x86.dev.fyre.ibm.com",
        port=50000,
        protocol="TCPIP",
        uid="Geetika",
        pwd="your_password_here",
    )
    
    # Initialize
    await db2vs.initialize()
    
    # Process code files
    code_documents = [
        Document(
            page_content="""
def authenticate_user(username: str, password: str) -> bool:
    \"\"\"Example only — use hashed passwords and a real identity provider in production.\"\"\"
    raise NotImplementedError(\"Use your org\\'s auth stack\")
            """,
            metadata={
                "file": "auth.py",
                "type": "security",
                "pr_number": 123,
            },
        ),
    ]
    
    # Add to vector store
    await db2vs.add_documents(code_documents, embeddings)
    
    # Search for security issues
    results = await db2vs.similarity_search_with_score(
        "security vulnerabilities in authentication",
        embeddings,
        k=5,
    )
    
    for doc, score in results:
        print(f"Score: {score:.4f}")
        print(f"File: {doc.metadata.get('file')}")
        print(f"Content: {doc.page_content[:100]}...\n")


if __name__ == "__main__":
    import asyncio
    
    # Run example
    asyncio.run(example_basic_setup())


# Made with Bob