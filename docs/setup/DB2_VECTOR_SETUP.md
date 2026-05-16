# IBM Db2 Vector Database Setup Guide

This guide provides comprehensive instructions for setting up IBM Db2 as a vector database for the IBM Dexter AI Code Reviewer project.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installing IBM Db2](#installing-ibm-db2)
3. [Installing IBM Db2 CLI Driver](#installing-ibm-db2-cli-driver)
4. [LangChain Db2 Integration](#langchain-db2-integration)
5. [Database Configuration](#database-configuration)
6. [Creating Vector Storage Schema](#creating-vector-storage-schema)
7. [Application Configuration](#application-configuration)
8. [Testing the Connection](#testing-the-connection)
9. [Performance Optimization](#performance-optimization)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

- Linux operating system (Ubuntu 20.04+ or RHEL 8+ recommended)
- Python 3.9 or higher
- IBM Db2 11.5 or higher installed
- Administrative access to Db2 instance
- At least 4GB RAM available for Db2
- 10GB+ disk space for database storage

## Installing IBM Db2

### Option 1: IBM Db2 Community Edition (Free)

1. **Download Db2 Community Edition:**
   ```bash
   # Visit IBM website to download
   # https://www.ibm.com/products/db2/trials
   
   # Or use wget (example for Linux x86_64)
   wget https://public.dhe.ibm.com/ibmdl/export/pub/software/data/db2/v11.5/linuxx64_expc/v11.5.8_linuxx64_expc.tar.gz
   ```

2. **Extract and Install:**
   ```bash
   tar -xzf v11.5.8_linuxx64_expc.tar.gz
   cd expc
   sudo ./db2_install
   ```

3. **Create Db2 Instance:**
   ```bash
   # Create instance owner user
   sudo useradd -m -d /home/db2inst1 db2inst1
   sudo passwd db2inst1
   
   # Create instance
   cd /opt/ibm/db2/V11.5/instance
   sudo ./db2icrt -u db2inst1 db2inst1
   ```

4. **Start Db2 Instance:**
   ```bash
   su - db2inst1
   db2start
   ```

### Option 2: IBM Db2 Docker Container

```bash
# Pull Db2 Docker image
docker pull ibmcom/db2:11.5.8.0

# Run Db2 container
docker run -itd \
  --name db2server \
  --privileged=true \
  -p 50000:50000 \
  -e LICENSE=accept \
  -e DB2INST1_PASSWORD=your_password \
  -e DBNAME=DEXTER \
  -v ~/db2data:/database \
  ibmcom/db2:11.5.8.0

# Wait for Db2 to start (may take 2-3 minutes)
docker logs -f db2server
```

## Installing IBM Db2 CLI Driver

The IBM Db2 CLI driver (`ibm_db`) is required for Python applications to connect to Db2.

### Linux Installation

1. **Install System Dependencies:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install -y gcc g++ python3-dev libxml2-dev libxslt-dev

   # RHEL/CentOS
   sudo yum install -y gcc gcc-c++ python3-devel libxml2-devel libxslt-devel
   ```

2. **Install IBM Db2 CLI Driver:**
   ```bash
   # Activate your Python virtual environment first
   source venv/bin/activate
   
   # Install ibm_db
   pip install ibm-db==3.2.3
   pip install ibm-db-sa==0.4.0
   ```

3. **Set Environment Variables:**
   ```bash
   # Add to ~/.bashrc or ~/.profile
   export IBM_DB_HOME=/opt/ibm/db2/V11.5
   export LD_LIBRARY_PATH=$IBM_DB_HOME/lib64:$LD_LIBRARY_PATH
   export PATH=$IBM_DB_HOME/bin:$PATH
   
   # Reload environment
   source ~/.bashrc
   ```

### macOS Installation

```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install ibm_db
pip install ibm-db==3.2.3
pip install ibm-db-sa==0.4.0
```

### Windows Installation

```bash
# Install Visual C++ Build Tools first
# Download from: https://visualstudio.microsoft.com/downloads/

# Install ibm_db
pip install ibm-db==3.2.3
pip install ibm-db-sa==0.4.0
```

## LangChain Db2 Integration

IBM Dexter now uses the official **langchain-db2** package for seamless integration with LangChain's ecosystem. This provides better compatibility, more features, and easier maintenance.

### Benefits of langchain-db2

1. **Official LangChain Support**: Maintained by the LangChain team with IBM collaboration
2. **Native Integration**: Works seamlessly with LangChain chains, agents, and tools
3. **Better Performance**: Optimized for vector similarity search
4. **Rich Features**: Document loaders, embeddings, and retrieval chains out-of-the-box
5. **Active Development**: Regular updates and bug fixes
6. **Type Safety**: Full type hints and better IDE support

### The db2vs Component

The **db2vs** component is a powerful feature of langchain-db2 that simplifies vector store setup and management:

#### What is db2vs?

`db2vs` (Db2 Vector Store) is a specialized component that:
- **Automatically creates** required tables and indexes
- **Manages schema** migrations and updates
- **Optimizes** vector operations for Db2
- **Handles** connection pooling efficiently
- **Provides** a simplified API for vector operations

#### Benefits of Using db2vs

1. **Zero Manual Setup**: No need to run SQL scripts manually
2. **Schema Management**: Automatically handles table creation and updates
3. **Optimized Performance**: Pre-configured indexes and settings
4. **Error Handling**: Built-in retry logic and connection management
5. **Type Safety**: Full Python type hints for better IDE support

#### Quick Start with db2vs

```python
from app.rag.db2vs_integration import Db2VSIntegration
from langchain.embeddings import HuggingFaceEmbeddings

# Initialize embeddings
embeddings = HuggingFaceEmbeddings()

# Initialize db2vs integration
db2vs = Db2VSIntegration(
    database="TESTDB",
    hostname="Geetika-5y420-x86.dev.fyre.ibm.com",
    port=50000,
    protocol="TCPIP",
    uid="Geetika",
    pwd="your_password_here",
    schema="DEXTER",
    table_name="VECTOR_EMBEDDINGS",
    embedding_dimension=384,
)

# Initialize (creates tables automatically)
await db2vs.initialize()

# Add documents
from langchain.schema import Document

documents = [
    Document(
        page_content="Python function for authentication",
        metadata={"language": "python", "type": "security"}
    ),
]

await db2vs.add_documents(documents, embeddings)

# Search
results = await db2vs.similarity_search(
    "security authentication",
    embeddings,
    k=5
)
```

#### Using the Setup Script

IBM Dexter includes a helper script that uses db2vs for easy setup:

```bash
# Test connection
python backend/scripts/setup_db2_vector.py --test-connection

# Prepare collections (tables created automatically by db2vs)
python backend/scripts/setup_db2_vector.py --create-tables

# Create all RAG collections
python backend/scripts/setup_db2_vector.py --create-collections

# Verify setup
python backend/scripts/setup_db2_vector.py --verify

# Load sample data into collections
python backend/scripts/setup_db2_vector.py --load-sample-data

# Run all steps (recommended)
python backend/scripts/setup_db2_vector.py --all
```

#### Configuration for db2vs with Collections

Update your `backend/.env` file:

```bash
# ============================================================================
# VECTOR DATABASE CONFIGURATION
# ============================================================================
DEXTER_VECTOR_DB_TYPE=db2
DEXTER_USE_LANGCHAIN_DB2=true

# ----------------------------------------------------------------------------
# IBM Db2 Vector Store Configuration
# ----------------------------------------------------------------------------
DEXTER_DB2_DATABASE=TESTDB
DEXTER_DB2_HOSTNAME=Geetika-5y420-x86.dev.fyre.ibm.com
DEXTER_DB2_PORT=50000
DEXTER_DB2_PROTOCOL=TCPIP
DEXTER_DB2_UID=Geetika
DEXTER_DB2_PWD=your_password_here

# Schema for all vector tables (db2vs will create tables as needed)
DEXTER_DB2_SCHEMA=DEXTER

# Table prefix (optional) - db2vs will create: DEXTER_CODE, DEXTER_DOCS, etc.
DEXTER_DB2_TABLE_PREFIX=DEXTER

# Embedding dimension (default: 384 for nomic-embed-text)
DEXTER_EMBEDDING_DIMENSION=384
```

## Collection-Based Architecture

IBM Dexter uses a **collection-based architecture** for organizing different types of documents in the vector database. Instead of a single table, db2vs automatically creates separate tables for each document type.

### Why Collections?

1. **Separation of Concerns**: Different document types (code, docs, PRs) in separate tables
2. **Better Performance**: Smaller, focused tables with optimized indexes
3. **Flexible Scaling**: Add new collections without affecting existing ones
4. **Type Safety**: Each collection has specific metadata schemas
5. **Easy Management**: Clear organization and maintenance

### Standard Collections

IBM Dexter defines the following standard collections for the RAG pipeline:

| Collection Name | Table Name | Purpose | Document Types |
|----------------|------------|---------|----------------|
| `code_embeddings` | `DEXTER.DEXTER_CODE_EMBEDDINGS` | Source code chunks | Python, Java, JavaScript, etc. |
| `docs_embeddings` | `DEXTER.DEXTER_DOCS_EMBEDDINGS` | Documentation | README, API docs, guides |
| `pr_history` | `DEXTER.DEXTER_PR_HISTORY` | Historical PR reviews | Past reviews, feedback |
| `architecture_docs` | `DEXTER.DEXTER_ARCHITECTURE_DOCS` | Architecture documents | Design docs, diagrams |
| `security_policies` | `DEXTER.DEXTER_SECURITY_POLICIES` | Security standards | OWASP, CWE, best practices |
| `compliance_rules` | `DEXTER.DEXTER_COMPLIANCE_RULES` | Compliance policies | SOC2, GDPR, HIPAA |
| `modernization_guides` | `DEXTER.DEXTER_MODERNIZATION_GUIDES` | Modernization docs | Migration guides, patterns |
| `test_patterns` | `DEXTER.DEXTER_TEST_PATTERNS` | Testing patterns | Unit tests, integration tests |
| `api_documentation` | `DEXTER.DEXTER_API_DOCUMENTATION` | API documentation | REST APIs, GraphQL schemas |

### How Collections Work

#### Automatic Table Creation

**No manual table creation needed!** db2vs automatically creates tables when you first add documents:

```python
from app.rag.vector_store import VectorStoreService

# Initialize service
service = VectorStoreService(vector_store_type="db2")

# Get collection (creates table automatically if needed)
code_store = await service.get_collection("code_embeddings")

# Add documents (table created on first add)
await code_store.add_documents(documents, embeddings)
```

#### Table Naming Convention

Tables are named using the pattern: `{SCHEMA}.{PREFIX}_{COLLECTION_NAME}`

Examples:
- Collection: `code_embeddings` → Table: `DEXTER.DEXTER_CODE_EMBEDDINGS`
- Collection: `docs_embeddings` → Table: `DEXTER.DEXTER_DOCS_EMBEDDINGS`
- Collection: `pr_history` → Table: `DEXTER.DEXTER_PR_HISTORY`

#### Working with Multiple Collections

```python
from app.rag.vector_store import VectorStoreService, CollectionNames

# Initialize service
service = VectorStoreService(vector_store_type="db2")

# Get different collections
code_store = await service.get_collection(CollectionNames.CODE_EMBEDDINGS)
docs_store = await service.get_collection(CollectionNames.DOCS_EMBEDDINGS)
security_store = await service.get_collection(CollectionNames.SECURITY_POLICIES)

# Each collection is independent
await code_store.add_documents(code_docs, embeddings)
await docs_store.add_documents(doc_docs, embeddings)
await security_store.add_documents(security_docs, embeddings)

# Search within specific collection
results = await code_store.similarity_search("authentication", embeddings, k=5)
```

#### Listing Collections

```python
# List all existing collections
collections = await service.list_collections()
print(f"Available collections: {collections}")

# Get collection info
info = service.get_collection_info("code_embeddings")
print(f"Collection info: {info}")
```

### Migration from Single Table

If you have an existing single-table setup, you can migrate to collections:

1. **Backup existing data**:
   ```sql
   -- Export existing data
   EXPORT TO vector_backup.del OF DEL
   SELECT * FROM DEXTER.VECTOR_EMBEDDINGS;
   ```

2. **Update configuration**:
   - Remove `DEXTER_DB2_TABLE` from `.env`
   - Add `DEXTER_DB2_TABLE_PREFIX=DEXTER`

3. **Create new collections**:
   ```bash
   python backend/scripts/setup_db2_vector.py --create-collections
   ```

4. **Migrate data** (if needed):
   ```python
   # Custom migration script to redistribute documents
   # into appropriate collections based on metadata
   ```

### Best Practices

1. **Use Standard Collections**: Stick to predefined collections when possible
2. **Consistent Naming**: Use lowercase with underscores (e.g., `my_collection`)
3. **Metadata Schema**: Define consistent metadata for each collection type
4. **Regular Cleanup**: Monitor and clean up unused collections
5. **Backup Strategy**: Backup collections separately for better recovery

### Performance Considerations

- **Smaller Tables**: Each collection is smaller, leading to faster queries
- **Targeted Indexes**: Indexes optimized for specific document types
- **Parallel Operations**: Multiple collections can be updated concurrently
- **Cache Efficiency**: Better cache hit rates with focused collections

### Installation

The langchain-db2 package is included in the project requirements:

```bash
# Install all dependencies including langchain-db2
cd backend
pip install -r requirements.txt

# Or install langchain-db2 separately
pip install langchain-db2
```

### Quick Start with LangChain

```python
from langchain_db2 import Db2VectorStore
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

# Initialize embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Create connection string
connection_string = (
    "db2+ibm_db://db2inst1:password@localhost:50000/DEXTER"
)

# Create vector store
vector_store = Db2VectorStore(
    embedding=embeddings,
    connection_string=connection_string,
    collection_name="code_embeddings",
)

# Add documents
documents = [
    Document(
        page_content="Python function for data processing",
        metadata={"language": "python", "type": "function"}
    ),
]
vector_store.add_documents(documents)

# Search
results = vector_store.similarity_search("data processing", k=5)
```

### Integration Modes

IBM Dexter supports two integration modes:

#### 1. LangChain Mode (Recommended)

Uses the official `langchain-db2` package:

```python
from backend.app.rag.db2_vector_store import Db2VectorStore

store = Db2VectorStore(
    database="DEXTER",
    hostname="localhost",
    port=50000,
    protocol="TCPIP",
    uid="db2inst1",
    pwd="your_password",
    use_langchain=True,  # Enable LangChain mode
)

# Check which mode is active
info = store.get_implementation_info()
print(f"Using LangChain: {info['using_langchain']}")
```

#### 2. Custom Mode (Fallback)

Uses raw `ibm_db` for backward compatibility:

```python
store = Db2VectorStore(
    database="DEXTER",
    hostname="localhost",
    port=50000,
    protocol="TCPIP",
    uid="db2inst1",
    pwd="your_password",
    use_langchain=False,  # Use custom implementation
)
```

### Advanced LangChain Examples

See `backend/app/rag/langchain_db2_integration.py` for comprehensive examples:

- Document processing and chunking
- Retrieval-Augmented Generation (RAG) chains
- Code review workflows
- Pull request analysis
- Similarity search with scoring

### Environment Configuration

Enable LangChain mode in your `.env` file:

```bash
# Use official LangChain Db2 integration
USE_LANGCHAIN_DB2=true
```

## Database Configuration

### 1. Create Database

```bash
# Connect as db2inst1
su - db2inst1

# Create database
db2 create database DEXTER using codeset UTF-8 territory US

# Connect to database
db2 connect to DEXTER
```

### 2. Configure Database Parameters

```sql
-- Increase log file size for better performance
db2 update db cfg for DEXTER using LOGFILSIZ 4096
db2 update db cfg for DEXTER using LOGPRIMARY 20
db2 update db cfg for DEXTER using LOGSECOND 40

-- Enable automatic storage
db2 update db cfg for DEXTER using AUTO_STORAGE YES

-- Set buffer pool size (adjust based on available memory)
db2 update db cfg for DEXTER using BUFFPAGE 10000

-- Commit changes
db2 terminate
db2stop
db2start
```

### 3. Configure Network Access

```bash
# Edit Db2 configuration
db2 update dbm cfg using SVCENAME 50000
db2 update dbm cfg using TCPIP YES

# Restart Db2
db2stop
db2start

# Verify listener
db2 get dbm cfg | grep SVCENAME
netstat -an | grep 50000
```

## Creating Vector Storage Schema

Run the SQL schema creation script to set up tables for vector storage.

### Using the Provided SQL Script

```bash
# Navigate to backend directory
cd backend

# Connect to Db2 and run schema
db2 connect to DEXTER
db2 -tvf db2_vector_schema.sql
db2 terminate
```

### Manual Schema Creation

```sql
-- Connect to database
CONNECT TO DEXTER;

-- Create schema
CREATE SCHEMA IF NOT EXISTS DEXTER;

-- Set current schema
SET SCHEMA DEXTER;

-- Create vector embeddings table
CREATE TABLE VECTOR_EMBEDDINGS (
    id VARCHAR(255) PRIMARY KEY NOT NULL,
    content CLOB(1M),
    embedding BLOB(1M),
    metadata VARCHAR(4000),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_vector_embeddings_id ON VECTOR_EMBEDDINGS(id);
CREATE INDEX idx_vector_embeddings_created ON VECTOR_EMBEDDINGS(created_at);

-- Grant permissions
GRANT ALL ON TABLE VECTOR_EMBEDDINGS TO USER db2inst1;

-- Verify table creation
SELECT TABNAME, TABSCHEMA FROM SYSCAT.TABLES 
WHERE TABSCHEMA = 'DEXTER';

COMMIT;
```

## Application Configuration

### 1. Update Environment Variables

Edit `backend/.env` file with collection-based configuration:

```bash
# ============================================================================
# VECTOR DATABASE CONFIGURATION
# ============================================================================
DEXTER_VECTOR_DB_TYPE=db2
DEXTER_USE_LANGCHAIN_DB2=true

# ----------------------------------------------------------------------------
# IBM Db2 Vector Store Configuration
# ----------------------------------------------------------------------------
DEXTER_DB2_DATABASE=TESTDB
DEXTER_DB2_HOSTNAME=Geetika-5y420-x86.dev.fyre.ibm.com
DEXTER_DB2_PORT=50000
DEXTER_DB2_PROTOCOL=TCPIP
DEXTER_DB2_UID=Geetika
DEXTER_DB2_PWD=your_password_here

# Schema for all vector tables (db2vs will create tables as needed)
DEXTER_DB2_SCHEMA=DEXTER

# Table prefix (optional) - db2vs will create: DEXTER_CODE, DEXTER_DOCS, etc.
# Leave empty for no prefix, or set to "DEXTER" for DEXTER_<collection_name>
DEXTER_DB2_TABLE_PREFIX=DEXTER

# Embedding dimension (default: 384 for nomic-embed-text)
DEXTER_EMBEDDING_DIMENSION=384
```

**Important Changes:**
- ❌ **Removed**: `DEXTER_DB2_TABLE` (no hardcoded table name)
- ✅ **Added**: `DEXTER_DB2_TABLE_PREFIX` (for collection naming)
- ✅ **Collections are created automatically** by db2vs when first used

**Note:** Replace `your_password_here` with your actual Db2 password.

### 2. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Verify Configuration

```python
# Test script: test_db2_connection.py
import ibm_db

conn_str = (
    "DATABASE=DEXTER;"
    "HOSTNAME=localhost;"
    "PORT=50000;"
    "PROTOCOL=TCPIP;"
    "UID=db2inst1;"
    "PWD=your_password;"
)

try:
    conn = ibm_db.connect(conn_str, "", "")
    print("✓ Successfully connected to Db2!")
    ibm_db.close(conn)
except Exception as e:
    print(f"✗ Connection failed: {e}")
```

## Testing the Connection

### 1. Basic Connection Test

```bash
# Run the test script
python test_db2_connection.py
```

### 2. Vector Store Test

```python
# test_vector_store.py
import asyncio
from backend.app.rag.vector_store_factory import get_vector_store

async def test_vector_store():
    # Get Db2 vector store
    store = get_vector_store()
    
    # Initialize
    await store.initialize()
    print("✓ Vector store initialized")
    
    # Add test document
    test_embedding = [0.1] * 384
    await store.add(
        document_id="test_1",
        content="This is a test document",
        embedding=test_embedding,
        metadata={"source": "test"}
    )
    print("✓ Document added")
    
    # Search
    results = await store.search(test_embedding, limit=5)
    print(f"✓ Search returned {len(results)} results")
    
    # Count
    count = await store.count()
    print(f"✓ Total documents: {count}")
    
    # Clean up
    await store.clear()
    print("✓ Store cleared")

if __name__ == "__main__":
    asyncio.run(test_vector_store())
```

Run the test:
```bash
python test_vector_store.py
```

## Performance Optimization

### 1. Database Tuning

```sql
-- Increase buffer pool for better caching
ALTER BUFFERPOOL IBMDEFAULTBP SIZE 50000;

-- Create tablespace with larger page size
CREATE TABLESPACE VECTOR_TS 
    PAGESIZE 32K 
    MANAGED BY AUTOMATIC STORAGE;

-- Move table to optimized tablespace
ALTER TABLE DEXTER.VECTOR_EMBEDDINGS 
    IN VECTOR_TS;

-- Update statistics for query optimization
RUNSTATS ON TABLE DEXTER.VECTOR_EMBEDDINGS 
    WITH DISTRIBUTION AND DETAILED INDEXES ALL;
```

### 2. Connection Pooling

The Db2VectorStore class manages connections efficiently. For high-concurrency scenarios, consider implementing connection pooling:

```python
# Example: Using SQLAlchemy with ibm_db_sa
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'db2+ibm_db://db2inst1:password@localhost:50000/DEXTER',
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600
)
```

### 3. Batch Operations

For bulk inserts, use the `add_batch` method:

```python
documents = [
    {
        "id": f"doc_{i}",
        "content": f"Document {i}",
        "embedding": [0.1] * 384,
        "metadata": {"index": i}
    }
    for i in range(1000)
]

await store.add_batch(documents)
```

### 4. Index Optimization

```sql
-- Create additional indexes based on query patterns
CREATE INDEX idx_vector_embeddings_metadata 
    ON DEXTER.VECTOR_EMBEDDINGS(metadata);

-- Reorganize table to improve performance
REORG TABLE DEXTER.VECTOR_EMBEDDINGS;

-- Update statistics after reorganization
RUNSTATS ON TABLE DEXTER.VECTOR_EMBEDDINGS;
```

## Troubleshooting

### Connection Issues

**Problem:** Cannot connect to Db2
```
SQL1336N  The remote host was not found.
```

**Solution:**
```bash
# Check if Db2 is running
db2 list active databases

# Verify network configuration
db2 get dbm cfg | grep SVCENAME
netstat -an | grep 50000

# Check firewall
sudo ufw allow 50000/tcp  # Ubuntu
sudo firewall-cmd --add-port=50000/tcp --permanent  # RHEL
```

### Authentication Issues

**Problem:** Authentication failed
```
SQL30082N  Security processing failed with reason "24" ("USERNAME AND/OR PASSWORD INVALID")
```

**Solution:**
```bash
# Reset password
sudo passwd db2inst1

# Verify user exists
db2 list db directory

# Check instance ownership
ls -la /home/db2inst1
```

### Driver Installation Issues

**Problem:** ibm_db installation fails
```
error: command 'gcc' failed with exit status 1
```

**Solution:**
```bash
# Install build dependencies
sudo apt-get install -y build-essential python3-dev

# Set environment variables
export IBM_DB_HOME=/opt/ibm/db2/V11.5
export LD_LIBRARY_PATH=$IBM_DB_HOME/lib64:$LD_LIBRARY_PATH

# Retry installation
pip install --no-cache-dir ibm-db
```

### Performance Issues

**Problem:** Slow query performance

**Solution:**
```sql
-- Check table statistics
SELECT * FROM SYSCAT.TABLES 
WHERE TABNAME = 'VECTOR_EMBEDDINGS';

-- Update statistics
RUNSTATS ON TABLE DEXTER.VECTOR_EMBEDDINGS 
    WITH DISTRIBUTION AND DETAILED INDEXES ALL;

-- Check for locks
SELECT * FROM SYSIBMADM.LOCKS_HELD;

-- Reorganize if needed
REORG TABLE DEXTER.VECTOR_EMBEDDINGS;
```

### Memory Issues

**Problem:** Out of memory errors

**Solution:**
```sql
-- Check current memory allocation
db2 get db cfg for DEXTER | grep -i memory

-- Increase buffer pool
ALTER BUFFERPOOL IBMDEFAULTBP SIZE 100000;

-- Adjust sort heap
db2 update db cfg for DEXTER using SORTHEAP 2048;
```

## Additional Resources

- [IBM Db2 Documentation](https://www.ibm.com/docs/en/db2)
- [IBM Db2 Python Driver](https://github.com/ibmdb/python-ibmdb)
- [IBM Db2 Performance Tuning](https://www.ibm.com/docs/en/db2/11.5?topic=performance-tuning)
- [IBM Db2 Community Forum](https://community.ibm.com/community/user/datamanagement/communities/community-home?CommunityKey=ea909850-39ea-4ac4-9512-8e2eb37ea09a)

## Support

For issues specific to IBM Dexter integration:
- Check the [GitHub Issues](https://github.com/your-org/ibm-dexter/issues)
- Review application logs: `backend/logs/`
- Enable debug logging: `DEXTER_LOG_LEVEL=DEBUG`

For Db2-specific issues:
- Consult IBM Db2 documentation
- Check Db2 diagnostic logs: `~/sqllib/db2dump/`
- Use Db2 diagnostic tools: `db2diag`, `db2pd`

---

**Made with Bob** - IBM Dexter AI Code Reviewer