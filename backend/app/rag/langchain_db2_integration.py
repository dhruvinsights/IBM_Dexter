"""LangChain Db2 Integration Examples and Utilities.

This module demonstrates how to use the official langchain-db2 package
for various RAG (Retrieval-Augmented Generation) workflows with IBM Db2.

Features:
- Document loading and processing
- Embeddings storage and retrieval
- Vector similarity search
- LangChain chains with Db2
- Advanced RAG patterns
"""

from __future__ import annotations

import logging
from typing import Any, List, Optional, Dict

logger = logging.getLogger(__name__)

# Try to import LangChain Db2 components
try:
    from langchain_db2 import Db2VectorStore, Db2
    from langchain.embeddings.base import Embeddings
    from langchain.schema import Document
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.chains import RetrievalQA
    from langchain.prompts import PromptTemplate
    LANGCHAIN_DB2_AVAILABLE = True
except ImportError:
    LANGCHAIN_DB2_AVAILABLE = False
    Db2VectorStore = None
    Db2 = None
    Embeddings = None
    Document = None


class LangChainDb2Integration:
    """Wrapper class for LangChain Db2 integration with helper methods."""

    def __init__(
        self,
        database: str,
        hostname: str,
        port: int,
        uid: str,
        pwd: str,
        schema: str = "DEXTER",
        collection_name: str = "code_embeddings",
    ):
        """Initialize LangChain Db2 integration.
        
        Args:
            database: Db2 database name
            hostname: Db2 server hostname
            port: Db2 server port
            uid: Database user ID
            pwd: Database password
            schema: Database schema name
            collection_name: Collection name for vector storage
        """
        if not LANGCHAIN_DB2_AVAILABLE:
            raise ImportError(
                "langchain-db2 is required. Install with: pip install langchain-db2"
            )
        
        self.database = database
        self.hostname = hostname
        self.port = port
        self.uid = uid
        self.pwd = pwd
        self.schema = schema
        self.collection_name = collection_name
        self._vector_store: Optional[Any] = None
        
        logger.info("LangChain Db2 integration initialized")

    def _get_connection_string(self) -> str:
        """Build Db2 connection string for LangChain."""
        return (
            f"db2+ibm_db://{self.uid}:{self.pwd}@"
            f"{self.hostname}:{self.port}/{self.database}"
        )

    def create_vector_store(
        self,
        embeddings: Embeddings,
        documents: Optional[List[Document]] = None,
    ) -> Any:
        """Create or get a Db2 vector store.
        
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
                    collection_name=self.collection_name,
                )
                logger.info(f"Created Db2 vector store with {len(documents)} documents")
            else:
                # Create empty store
                self._vector_store = Db2VectorStore(
                    embedding=embeddings,
                    connection_string=connection_string,
                    collection_name=self.collection_name,
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
        vector_store = self.create_vector_store(embeddings)
        results = await vector_store.asimilarity_search_with_score(query, k=k)
        logger.info(f"Found {len(results)} similar documents with scores")
        return results

    def create_retrieval_chain(
        self,
        embeddings: Embeddings,
        llm: Any,
        chain_type: str = "stuff",
    ) -> Any:
        """Create a RetrievalQA chain with Db2 vector store.
        
        Args:
            embeddings: Embeddings instance
            llm: Language model instance
            chain_type: Chain type (stuff, map_reduce, refine, map_rerank)
            
        Returns:
            RetrievalQA chain
        """
        vector_store = self.create_vector_store(embeddings)
        retriever = vector_store.as_retriever(search_kwargs={"k": 5})
        
        chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type=chain_type,
            retriever=retriever,
            return_source_documents=True,
        )
        
        logger.info(f"Created {chain_type} retrieval chain")
        return chain


class CodeDocumentProcessor:
    """Process code documents for storage in Db2 vector store."""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        """Initialize code document processor.
        
        Args:
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
        )
        logger.info("Code document processor initialized")

    def process_code_file(
        self,
        file_path: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        """Process a code file into documents.
        
        Args:
            file_path: Path to the code file
            content: File content
            metadata: Additional metadata
            
        Returns:
            List of Document objects
        """
        # Prepare metadata
        doc_metadata = {
            "source": file_path,
            "type": "code",
            **(metadata or {}),
        }
        
        # Split into chunks
        chunks = self.text_splitter.split_text(content)
        
        # Create documents
        documents = [
            Document(
                page_content=chunk,
                metadata={
                    **doc_metadata,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                },
            )
            for i, chunk in enumerate(chunks)
        ]
        
        logger.info(f"Processed {file_path} into {len(documents)} chunks")
        return documents

    def process_pull_request(
        self,
        pr_number: int,
        title: str,
        description: str,
        files_changed: List[Dict[str, str]],
    ) -> List[Document]:
        """Process a pull request into documents.
        
        Args:
            pr_number: Pull request number
            title: PR title
            description: PR description
            files_changed: List of changed files with content
            
        Returns:
            List of Document objects
        """
        documents = []
        
        # Add PR overview document
        pr_overview = f"# Pull Request #{pr_number}: {title}\n\n{description}"
        documents.append(
            Document(
                page_content=pr_overview,
                metadata={
                    "source": f"PR#{pr_number}",
                    "type": "pull_request_overview",
                    "pr_number": pr_number,
                },
            )
        )
        
        # Process each changed file
        for file_info in files_changed:
            file_docs = self.process_code_file(
                file_path=file_info["path"],
                content=file_info["content"],
                metadata={
                    "pr_number": pr_number,
                    "change_type": file_info.get("status", "modified"),
                },
            )
            documents.extend(file_docs)
        
        logger.info(f"Processed PR#{pr_number} into {len(documents)} documents")
        return documents


# Example usage functions

async def example_basic_usage():
    """Example: Basic document storage and retrieval."""
    from langchain.embeddings import HuggingFaceEmbeddings
    
    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    # Initialize Db2 integration
    db2_integration = LangChainDb2Integration(
        database="DEXTER",
        hostname="localhost",
        port=50000,
        uid="db2inst1",
        pwd="your_password",
    )
    
    # Create sample documents
    documents = [
        Document(
            page_content="This is a Python function that calculates fibonacci numbers.",
            metadata={"language": "python", "type": "function"},
        ),
        Document(
            page_content="This is a JavaScript async function for API calls.",
            metadata={"language": "javascript", "type": "function"},
        ),
    ]
    
    # Add documents
    await db2_integration.add_documents(documents, embeddings)
    
    # Search
    results = await db2_integration.similarity_search(
        "How to make API calls?",
        embeddings,
        k=3,
    )
    
    for doc in results:
        print(f"Content: {doc.page_content}")
        print(f"Metadata: {doc.metadata}\n")


async def example_code_review_rag():
    """Example: RAG pipeline for code review."""
    from langchain.embeddings import HuggingFaceEmbeddings
    from langchain.llms import Ollama
    
    # Initialize components
    embeddings = HuggingFaceEmbeddings()
    llm = Ollama(model="llama3")
    
    db2_integration = LangChainDb2Integration(
        database="DEXTER",
        hostname="localhost",
        port=50000,
        uid="db2inst1",
        pwd="your_password",
    )
    
    # Process code files
    processor = CodeDocumentProcessor()
    documents = processor.process_code_file(
        file_path="src/app.py",
        content="def hello():\n    print('Hello, World!')",
        metadata={"project": "dexter"},
    )
    
    # Add to vector store
    await db2_integration.add_documents(documents, embeddings)
    
    # Create retrieval chain
    qa_chain = db2_integration.create_retrieval_chain(
        embeddings=embeddings,
        llm=llm,
        chain_type="stuff",
    )
    
    # Ask questions
    result = qa_chain({"query": "What does the hello function do?"})
    print(f"Answer: {result['result']}")
    print(f"Sources: {result['source_documents']}")


async def example_advanced_search():
    """Example: Advanced search with filters and scoring."""
    from langchain.embeddings import HuggingFaceEmbeddings
    
    embeddings = HuggingFaceEmbeddings()
    
    db2_integration = LangChainDb2Integration(
        database="DEXTER",
        hostname="localhost",
        port=50000,
        uid="db2inst1",
        pwd="your_password",
    )
    
    # Search with scores
    results = await db2_integration.similarity_search_with_score(
        query="security vulnerabilities in authentication",
        embeddings=embeddings,
        k=5,
    )
    
    for doc, score in results:
        print(f"Score: {score:.4f}")
        print(f"Content: {doc.page_content[:100]}...")
        print(f"Metadata: {doc.metadata}\n")


# Custom prompt template for code review
CODE_REVIEW_PROMPT = PromptTemplate(
    template="""You are an expert code reviewer. Based on the following code context, 
provide a detailed review focusing on:
1. Code quality and best practices
2. Potential bugs or issues
3. Security concerns
4. Performance optimizations
5. Suggestions for improvement

Context:
{context}

Code to review:
{question}

Detailed Review:""",
    input_variables=["context", "question"],
)


def create_code_review_chain(
    db2_integration: LangChainDb2Integration,
    embeddings: Embeddings,
    llm: Any,
) -> Any:
    """Create a specialized code review chain.
    
    Args:
        db2_integration: Db2 integration instance
        embeddings: Embeddings instance
        llm: Language model instance
        
    Returns:
        Custom RetrievalQA chain for code review
    """
    vector_store = db2_integration.create_vector_store(embeddings)
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": CODE_REVIEW_PROMPT},
    )
    
    return chain


# Made with Bob