#!/usr/bin/env python3
"""Setup script for IBM Db2 Vector Store.

This script helps you:
1. Test Db2 connection
2. Create vector store tables using db2vs component
3. Verify setup
4. Load sample data for testing

Usage:
    python backend/scripts/setup_db2_vector.py --test-connection
    python backend/scripts/setup_db2_vector.py --create-tables
    python backend/scripts/setup_db2_vector.py --verify
    python backend/scripts/setup_db2_vector.py --load-sample-data
    python backend/scripts/setup_db2_vector.py --all
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.core.config import get_settings
from app.rag.db2vs_integration import Db2VSIntegration, DB2VS_AVAILABLE

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def print_success(text: str):
    """Print success message."""
    print(f"✓ {text}")


def print_error(text: str):
    """Print error message."""
    print(f"✗ {text}")


def print_info(text: str):
    """Print info message."""
    print(f"ℹ {text}")


async def test_connection() -> bool:
    """Test connection to Db2 database.
    
    Returns:
        True if connection successful, False otherwise
    """
    print_header("Testing Db2 Connection")
    
    settings = get_settings()
    
    # Display connection info (without password)
    print_info("Connection Details:")
    print(f"  Database: {settings.db2_database}")
    print(f"  Hostname: {settings.db2_hostname}")
    print(f"  Port: {settings.db2_port}")
    print(f"  Username: {settings.db2_uid}")
    print(f"  Schema: {settings.db2_schema}")
    print()
    
    if not DB2VS_AVAILABLE:
        print_error("langchain-db2 is not installed!")
        print_info("Install with: pip install langchain-db2")
        return False
    
    try:
        # Try to import ibm_db for direct connection test
        import ibm_db
        
        conn_str = (
            f"DATABASE={settings.db2_database};"
            f"HOSTNAME={settings.db2_hostname};"
            f"PORT={settings.db2_port};"
            f"PROTOCOL={settings.db2_protocol};"
            f"UID={settings.db2_uid};"
            f"PWD={settings.db2_pwd};"
        )
        
        print_info("Attempting to connect...")
        conn = ibm_db.connect(conn_str, "", "")
        
        if conn:
            print_success("Successfully connected to Db2!")
            
            # Get server info
            server_info = ibm_db.server_info(conn)
            print_info(f"Server Version: {server_info.DBMS_VER}")
            print_info(f"Server Name: {server_info.DBMS_NAME}")
            
            ibm_db.close(conn)
            return True
        else:
            print_error("Failed to connect to Db2")
            return False
            
    except ImportError:
        print_error("ibm_db is not installed!")
        print_info("Install with: pip install ibm-db")
        return False
    except Exception as e:
        print_error(f"Connection failed: {e}")
        print_info("Please check your credentials in backend/.env")
        return False


async def create_tables() -> bool:
    """Create vector store tables using db2vs component.
    
    Note: db2vs automatically creates tables when first document is added.
    This function prepares the collections for use.
    
    Returns:
        True if tables created successfully, False otherwise
    """
    print_header("Preparing Vector Store Collections")
    
    if not DB2VS_AVAILABLE:
        print_error("langchain-db2 is not installed!")
        return False
    
    settings = get_settings()
    
    try:
        from app.rag.vector_store import CollectionNames
        
        print_info("Preparing collections for RAG pipeline...")
        print_info(f"Schema: {settings.db2_schema}")
        print_info(f"Table Prefix: {getattr(settings, 'db2_table_prefix', 'DEXTER')}")
        print_info(f"Embedding Dimension: {settings.embedding_dimension}")
        print()
        
        # Get all predefined collections
        collections = CollectionNames.all()
        
        print_info(f"Collections to be created (on first use):")
        for collection in collections:
            table_prefix = getattr(settings, 'db2_table_prefix', 'DEXTER')
            table_name = f"{table_prefix}_{collection.upper()}" if table_prefix else collection.upper()
            print(f"  • {collection:30s} → {settings.db2_schema}.{table_name}")
        
        print()
        print_success("Collections prepared successfully!")
        print_info("Tables will be created automatically by db2vs when first document is added")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to prepare collections: {e}")
        return False


async def create_rag_collections() -> bool:
    """Create all necessary collections for RAG pipeline.
    
    Returns:
        True if collections created successfully, False otherwise
    """
    print_header("Creating RAG Collections")
    
    if not DB2VS_AVAILABLE:
        print_error("langchain-db2 is not installed!")
        return False
    
    settings = get_settings()
    
    try:
        from app.rag.vector_store import VectorStoreService, CollectionNames
        
        # Initialize vector store service
        service = VectorStoreService(vector_store_type="db2")
        
        print_info("Creating collections for RAG pipeline...")
        print()
        
        # Create each collection
        collections = CollectionNames.all()
        created_count = 0
        
        for collection_name in collections:
            try:
                collection = await service.get_collection(collection_name, create_if_missing=True)
                table_prefix = getattr(settings, 'db2_table_prefix', 'DEXTER')
                table_name = f"{table_prefix}_{collection_name.upper()}" if table_prefix else collection_name.upper()
                print_success(f"Collection '{collection_name}' ready (table: {settings.db2_schema}.{table_name})")
                created_count += 1
            except Exception as e:
                print_error(f"Failed to create collection '{collection_name}': {e}")
        
        print()
        print_success(f"Created {created_count}/{len(collections)} collections!")
        print_info("Tables will be created automatically when first document is added")
        
        return created_count > 0
        
    except Exception as e:
        print_error(f"Failed to create RAG collections: {e}")
        return False


async def verify_setup() -> bool:
    """Verify that the vector store is set up correctly.
    
    Returns:
        True if setup is valid, False otherwise
    """
    print_header("Verifying Vector Store Setup")
    
    if not DB2VS_AVAILABLE:
        print_error("langchain-db2 is not installed!")
        return False
    
    settings = get_settings()
    
    try:
        import ibm_db
        from app.rag.vector_store import CollectionNames
        
        conn_str = (
            f"DATABASE={settings.db2_database};"
            f"HOSTNAME={settings.db2_hostname};"
            f"PORT={settings.db2_port};"
            f"PROTOCOL={settings.db2_protocol};"
            f"UID={settings.db2_uid};"
            f"PWD={settings.db2_pwd};"
        )
        
        conn = ibm_db.connect(conn_str, "", "")
        
        # Check if schema exists
        schema_query = f"""
        SELECT SCHEMANAME FROM SYSCAT.SCHEMATA
        WHERE SCHEMANAME = '{settings.db2_schema}'
        """
        stmt = ibm_db.exec_immediate(conn, schema_query)
        row = ibm_db.fetch_assoc(stmt)
        
        if row:
            print_success(f"Schema '{settings.db2_schema}' exists")
        else:
            print_error(f"Schema '{settings.db2_schema}' not found")
            ibm_db.close(conn)
            return False
        
        # Check for existing collection tables
        table_prefix = getattr(settings, 'db2_table_prefix', 'DEXTER')
        pattern = f"{table_prefix}_%"
        
        tables_query = f"""
        SELECT TABNAME FROM SYSCAT.TABLES
        WHERE TABSCHEMA = '{settings.db2_schema}'
        AND TABNAME LIKE '{pattern}'
        """
        stmt = ibm_db.exec_immediate(conn, tables_query)
        
        existing_tables = []
        while ibm_db.fetch_row(stmt):
            table_name = ibm_db.result(stmt, 0)
            existing_tables.append(table_name)
        
        if existing_tables:
            print_success(f"Found {len(existing_tables)} collection table(s):")
            for table in existing_tables:
                # Get row count for each table
                count_query = f"SELECT COUNT(*) as CNT FROM {settings.db2_schema}.{table}"
                count_stmt = ibm_db.exec_immediate(conn, count_query)
                count_row = ibm_db.fetch_assoc(count_stmt)
                count = count_row['CNT'] if count_row else 0
                print(f"  • {table:40s} ({count} documents)")
        else:
            print_info("No collection tables found yet (will be created on first use)")
        
        ibm_db.close(conn)
        print_success("Vector store setup verified!")
        return True
        
    except Exception as e:
        print_error(f"Verification failed: {e}")
        return False


async def load_sample_data() -> bool:
    """Load sample data into the vector store for testing.
    
    Returns:
        True if data loaded successfully, False otherwise
    """
    print_header("Loading Sample Data into Collections")
    
    if not DB2VS_AVAILABLE:
        print_error("langchain-db2 is not installed!")
        return False
    
    settings = get_settings()
    
    try:
        from langchain.embeddings import HuggingFaceEmbeddings
        from langchain.schema import Document
        from app.rag.vector_store import VectorStoreService
        
        # Initialize embeddings
        print_info("Initializing embeddings model...")
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Initialize vector store service
        service = VectorStoreService(vector_store_type="db2")
        
        # Load sample data into code_embeddings collection
        print_info("\nLoading sample code embeddings...")
        code_collection = await service.get_collection("code_embeddings")
        
        code_docs = [
            Document(
                page_content="This is a Python function that implements authentication logic.",
                metadata={"language": "python", "type": "security", "file": "auth.py"},
            ),
            Document(
                page_content="This JavaScript function handles API requests with error handling.",
                metadata={"language": "javascript", "type": "api", "file": "api.js"},
            ),
        ]
        
        ids = await code_collection.add_documents(code_docs, embeddings)
        print_success(f"Loaded {len(ids)} code documents")
        
        # Load sample data into docs_embeddings collection
        print_info("\nLoading sample documentation...")
        docs_collection = await service.get_collection("docs_embeddings")
        
        doc_docs = [
            Document(
                page_content="API documentation for authentication endpoints and security best practices.",
                metadata={"type": "api_docs", "category": "security"},
            ),
        ]
        
        ids = await docs_collection.add_documents(doc_docs, embeddings)
        print_success(f"Loaded {len(ids)} documentation documents")
        
        # Test search on code collection
        print_info("\nTesting similarity search on code_embeddings...")
        results = await code_collection.similarity_search(
            "authentication security",
            embeddings,
            k=2,
        )
        
        print_success(f"Found {len(results)} similar documents")
        for i, doc in enumerate(results, 1):
            print(f"\n  Result {i}:")
            print(f"    Content: {doc.page_content[:60]}...")
            print(f"    Metadata: {doc.metadata}")
        
        return True
        
    except ImportError as e:
        print_error(f"Missing dependency: {e}")
        print_info("Install with: pip install langchain sentence-transformers")
        return False
    except Exception as e:
        print_error(f"Failed to load sample data: {e}")
        return False


async def run_all():
    """Run all setup steps."""
    print_header("IBM Db2 Vector Store Setup with Collections")
    
    # Test connection
    if not await test_connection():
        print_error("Setup aborted due to connection failure")
        return False
    
    # Prepare collections
    if not await create_tables():
        print_error("Setup aborted due to collection preparation failure")
        return False
    
    # Create RAG collections
    if not await create_rag_collections():
        print_error("RAG collection creation failed")
        return False
    
    # Verify setup
    if not await verify_setup():
        print_error("Setup verification failed")
        return False
    
    # Load sample data
    if not await load_sample_data():
        print_error("Sample data loading failed")
        return False
    
    print_header("Setup Complete!")
    print_success("Your Db2 vector store with collections is ready to use!")
    print_info("\nNext steps:")
    print("  1. Update DEXTER_DB2_PWD in backend/.env with your password")
    print("  2. Set DEXTER_VECTOR_DB_TYPE=db2 in backend/.env")
    print("  3. Set DEXTER_USE_LANGCHAIN_DB2=true in backend/.env")
    print("  4. Start the backend: python backend/main.py")
    print()
    print_info("Collections created:")
    print("  • code_embeddings - Source code chunks")
    print("  • docs_embeddings - Documentation")
    print("  • pr_history - Historical PR reviews")
    print("  • architecture_docs - Architecture documents")
    print("  • security_policies - Security standards")
    print("  • And more...")
    
    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Setup IBM Db2 Vector Store for IBM Dexter with Collection Support"
    )
    parser.add_argument(
        "--test-connection",
        action="store_true",
        help="Test connection to Db2 database"
    )
    parser.add_argument(
        "--create-tables",
        action="store_true",
        help="Prepare vector store collections (tables created automatically by db2vs)"
    )
    parser.add_argument(
        "--create-collections",
        action="store_true",
        help="Create all RAG collections for the pipeline"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify vector store setup"
    )
    parser.add_argument(
        "--load-sample-data",
        action="store_true",
        help="Load sample data into collections for testing"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all setup steps (recommended)"
    )
    
    args = parser.parse_args()
    
    # If no arguments, show help
    if not any(vars(args).values()):
        parser.print_help()
        print("\n" + "=" * 70)
        print("QUICK START:")
        print("  python backend/scripts/setup_db2_vector.py --all")
        print("=" * 70)
        return
    
    # Run requested operations
    try:
        if args.all:
            success = asyncio.run(run_all())
        else:
            success = True
            if args.test_connection:
                success = success and asyncio.run(test_connection())
            if args.create_tables:
                success = success and asyncio.run(create_tables())
            if args.create_collections:
                success = success and asyncio.run(create_rag_collections())
            if args.verify:
                success = success and asyncio.run(verify_setup())
            if args.load_sample_data:
                success = success and asyncio.run(load_sample_data())
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


# Made with Bob