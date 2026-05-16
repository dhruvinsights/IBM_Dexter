-- ============================================================================
-- IBM Db2 Vector Storage Schema for IBM Dexter AI Code Reviewer
-- ============================================================================
-- This script creates the necessary database objects for storing embeddings
-- and performing vector similarity search in IBM Db2.
--
-- Prerequisites:
--   - IBM Db2 11.5 or higher
--   - Database DEXTER must exist
--   - User must have CREATE TABLE, CREATE INDEX, and CREATE FUNCTION privileges
--
-- Usage:
--   db2 connect to DEXTER
--   db2 -tvf db2_vector_schema.sql
--   db2 terminate
-- ============================================================================

-- Connect to the database
CONNECT TO DEXTER;

-- ============================================================================
-- 1. CREATE SCHEMA
-- ============================================================================

-- Create the DEXTER schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS DEXTER;

-- Set the current schema
SET SCHEMA DEXTER;

-- ============================================================================
-- 2. CREATE VECTOR EMBEDDINGS TABLE
-- ============================================================================

-- Drop table if exists (for clean reinstall)
-- DROP TABLE IF EXISTS VECTOR_EMBEDDINGS;

-- Create the main table for storing document embeddings
CREATE TABLE VECTOR_EMBEDDINGS (
    -- Unique identifier for each document
    id VARCHAR(255) PRIMARY KEY NOT NULL,
    
    -- Document content (up to 1MB)
    content CLOB(1M),
    
    -- Embedding vector stored as BLOB (JSON serialized)
    embedding BLOB(1M) NOT NULL,
    
    -- Metadata stored as JSON string (up to 4000 chars)
    metadata VARCHAR(4000),
    
    -- Timestamp when record was created
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Timestamp when record was last updated
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
)
IN USERSPACE1;

-- Add table comment
COMMENT ON TABLE VECTOR_EMBEDDINGS IS 
'Stores document embeddings for semantic search in IBM Dexter AI Code Reviewer';

-- Add column comments
COMMENT ON COLUMN VECTOR_EMBEDDINGS.id IS 
'Unique identifier for the document';

COMMENT ON COLUMN VECTOR_EMBEDDINGS.content IS 
'Full text content of the document';

COMMENT ON COLUMN VECTOR_EMBEDDINGS.embedding IS 
'Vector embedding stored as JSON-serialized BLOB';

COMMENT ON COLUMN VECTOR_EMBEDDINGS.metadata IS 
'Additional metadata stored as JSON string';

COMMENT ON COLUMN VECTOR_EMBEDDINGS.created_at IS 
'Timestamp when the record was created';

COMMENT ON COLUMN VECTOR_EMBEDDINGS.updated_at IS 
'Timestamp when the record was last updated';

-- ============================================================================
-- 3. CREATE INDEXES
-- ============================================================================

-- Index on primary key (automatically created, but explicit for clarity)
-- CREATE UNIQUE INDEX idx_vector_embeddings_pk ON VECTOR_EMBEDDINGS(id);

-- Index on created_at for time-based queries
CREATE INDEX idx_vector_embeddings_created 
ON VECTOR_EMBEDDINGS(created_at DESC);

-- Index on updated_at for finding recently modified records
CREATE INDEX idx_vector_embeddings_updated 
ON VECTOR_EMBEDDINGS(updated_at DESC);

-- ============================================================================
-- 4. CREATE TRIGGERS
-- ============================================================================

-- Trigger to automatically update the updated_at timestamp
CREATE OR REPLACE TRIGGER trg_vector_embeddings_update
BEFORE UPDATE ON VECTOR_EMBEDDINGS
REFERENCING NEW AS n OLD AS o
FOR EACH ROW
BEGIN ATOMIC
    SET n.updated_at = CURRENT_TIMESTAMP;
END;

-- ============================================================================
-- 5. CREATE HELPER FUNCTIONS (Optional)
-- ============================================================================

-- Note: Db2 doesn't support user-defined functions for complex operations
-- like cosine similarity in SQL easily. The application layer handles
-- vector similarity calculations using Python.

-- ============================================================================
-- 6. GRANT PERMISSIONS
-- ============================================================================

-- Grant all privileges on the table to the instance owner
GRANT ALL ON TABLE VECTOR_EMBEDDINGS TO USER db2inst1;

-- Grant select, insert, update, delete to application users
-- Uncomment and modify as needed for your environment
-- GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE VECTOR_EMBEDDINGS TO USER dexter_app;

-- ============================================================================
-- 7. SAMPLE QUERIES
-- ============================================================================

-- Count total documents
-- SELECT COUNT(*) as total_documents FROM VECTOR_EMBEDDINGS;

-- Get recent documents
-- SELECT id, content, created_at 
-- FROM VECTOR_EMBEDDINGS 
-- ORDER BY created_at DESC 
-- FETCH FIRST 10 ROWS ONLY;

-- Search by ID
-- SELECT * FROM VECTOR_EMBEDDINGS WHERE id = 'doc_123';

-- Get documents with metadata
-- SELECT id, content, metadata, created_at 
-- FROM VECTOR_EMBEDDINGS 
-- WHERE metadata IS NOT NULL;

-- Delete old documents (older than 90 days)
-- DELETE FROM VECTOR_EMBEDDINGS 
-- WHERE created_at < CURRENT_TIMESTAMP - 90 DAYS;

-- ============================================================================
-- 8. PERFORMANCE OPTIMIZATION
-- ============================================================================

-- Update table statistics for query optimizer
RUNSTATS ON TABLE DEXTER.VECTOR_EMBEDDINGS 
WITH DISTRIBUTION AND DETAILED INDEXES ALL;

-- Reorganize table to improve performance (run periodically)
-- REORG TABLE DEXTER.VECTOR_EMBEDDINGS;

-- ============================================================================
-- 9. BACKUP AND MAINTENANCE
-- ============================================================================

-- Create a backup table (for testing or migration)
-- CREATE TABLE VECTOR_EMBEDDINGS_BACKUP LIKE VECTOR_EMBEDDINGS;
-- INSERT INTO VECTOR_EMBEDDINGS_BACKUP SELECT * FROM VECTOR_EMBEDDINGS;

-- Export data to file
-- EXPORT TO vector_embeddings.del OF DEL 
-- SELECT * FROM VECTOR_EMBEDDINGS;

-- Import data from file
-- IMPORT FROM vector_embeddings.del OF DEL 
-- INSERT INTO VECTOR_EMBEDDINGS;

-- ============================================================================
-- 10. VERIFICATION
-- ============================================================================

-- Verify table creation
SELECT 
    TABNAME as table_name,
    TABSCHEMA as schema_name,
    TYPE as table_type,
    STATUS as status,
    CREATE_TIME as created_at
FROM SYSCAT.TABLES 
WHERE TABSCHEMA = 'DEXTER' 
  AND TABNAME = 'VECTOR_EMBEDDINGS';

-- Verify indexes
SELECT 
    INDNAME as index_name,
    TABNAME as table_name,
    UNIQUERULE as is_unique,
    COLNAMES as columns,
    CREATE_TIME as created_at
FROM SYSCAT.INDEXES 
WHERE TABSCHEMA = 'DEXTER' 
  AND TABNAME = 'VECTOR_EMBEDDINGS';

-- Verify triggers
SELECT 
    TRIGNAME as trigger_name,
    TABNAME as table_name,
    TRIGTIME as trigger_time,
    TRIGEVENT as trigger_event,
    CREATE_TIME as created_at
FROM SYSCAT.TRIGGERS 
WHERE TABSCHEMA = 'DEXTER' 
  AND TABNAME = 'VECTOR_EMBEDDINGS';

-- Check table size and row count
SELECT 
    TABNAME as table_name,
    CARD as row_count,
    NPAGES as num_pages,
    FPAGES as formatted_pages,
    STATS_TIME as last_stats_update
FROM SYSCAT.TABLES 
WHERE TABSCHEMA = 'DEXTER' 
  AND TABNAME = 'VECTOR_EMBEDDINGS';

-- ============================================================================
-- 11. CLEANUP (Use with caution!)
-- ============================================================================

-- Drop all objects (uncomment to use)
-- DROP TRIGGER DEXTER.trg_vector_embeddings_update;
-- DROP TABLE DEXTER.VECTOR_EMBEDDINGS;
-- DROP SCHEMA DEXTER RESTRICT;

-- ============================================================================
-- COMMIT CHANGES
-- ============================================================================

COMMIT WORK;

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================

-- Display success message
VALUES ('IBM Db2 Vector Storage Schema created successfully!');
VALUES ('Schema: DEXTER');
VALUES ('Table: VECTOR_EMBEDDINGS');
VALUES ('Ready for use with IBM Dexter AI Code Reviewer');

-- Disconnect
TERMINATE;

-- ============================================================================
-- END OF SCRIPT
-- ============================================================================
-- Made with Bob - IBM Dexter AI Code Reviewer
-- ============================================================================