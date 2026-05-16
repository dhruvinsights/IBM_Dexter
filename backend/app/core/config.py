"""Application configuration management for IBM Dexter."""

from functools import lru_cache
from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# ============================================================================
# Optional LLM Provider Imports - Gracefully handle missing packages
# ============================================================================

# Check for OpenAI availability
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Check for Anthropic availability
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# Check for Cohere availability
try:
    import cohere
    COHERE_AVAILABLE = True
except ImportError:
    COHERE_AVAILABLE = False

# Check for IBM Watsonx availability
try:
    from ibm_watsonx_ai import Credentials
    WATSONX_AVAILABLE = True
except ImportError:
    WATSONX_AVAILABLE = False

# Check for llama-cpp-python availability
try:
    import llama_cpp
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False

# Check for IBM Db2 vector store availability
try:
    from langchain_db2 import Db2VectorStore
    DB2_AVAILABLE = True
except ImportError:
    DB2_AVAILABLE = False

# Check for Celery availability
try:
    import celery
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False

# Check for Redis availability
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    app_name: str = "IBM Dexter Backend"
    app_version: str = "0.1.0"
    app_env: Literal["development", "test", "staging", "production"] = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False

    database_url: str = "sqlite+aiosqlite:///./dexter.db"
    test_database_url: str = "sqlite+aiosqlite:///./dexter_test.db"
    database_echo: bool = False
    database_pool_size: int = 5
    database_max_overflow: int = 10

    redis_url: str = "redis://localhost:6379/0"

    jwt_secret_key: str = Field("change-me-in-production", min_length=16)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_minutes: int = 60 * 24 * 7

    api_key_header_name: str = "X-API-Key"
    api_key: str = "dexter-local-api-key"

    github_token: str = ""
    github_webhook_secret: str = "github-webhook-secret"
    gitlab_token: str = ""
    gitlab_webhook_secret: str = "gitlab-webhook-secret"

    # Legacy AI provider settings (deprecated, use LLM_PROVIDER instead)
    ai_provider: Literal["openai", "watsonx", "anthropic", "mock"] = "mock"
    
    # LLM Configuration
    llm_provider: str = "ollama"  # Default to Ollama for local testing
    
    # Ollama Configuration (Primary for testing)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"  # Default model
    
    # IBM Watsonx Configuration (Secondary)
    watsonx_api_key: Optional[str] = None
    watsonx_project_id: Optional[str] = None
    watsonx_url: str = "https://us-south.ml.cloud.ibm.com"
    watsonx_model: str = "ibm/granite-13b-chat-v2"
    
    # Optional API Keys (User-provided)
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-sonnet-20240229"
    cohere_api_key: Optional[str] = None
    cohere_model: str = "command-r-plus"
    
    # LLM Settings
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2000
    llm_timeout: int = 60

    # Vector Database Configuration
    vector_db_type: str = "db2"  # Options: inmemory, db2 (IBM Db2 via langchain-db2)
    use_langchain_db2: bool = True  # Use LangChain's official Db2 integration (db2vs component)
    
    # IBM Db2 Vector Database Configuration
    db2_database: str = "TESTDB"
    db2_hostname: str = "Geetika-5y420-x86.dev.fyre.ibm.com"
    db2_port: int = 50000
    db2_protocol: str = "TCPIP"
    db2_uid: str = "Geetika"
    db2_pwd: str = ""
    db2_schema: str = "DEXTER"
    db2_table_prefix: str = "DEXTER"  # Table prefix for collections (e.g., DEXTER_CODE_EMBEDDINGS)
    embedding_dimension: int = 384  # Embedding dimension (default: 384 for nomic-embed-text)

    cors_origins: str = "http://localhost:3000,http://localhost:8000"

    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="DEXTER_",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Return normalized CORS origins."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def is_provider_available(self, provider: str) -> bool:
        """Check if a specific LLM provider is available."""
        availability_map = {
            "openai": OPENAI_AVAILABLE,
            "anthropic": ANTHROPIC_AVAILABLE,
            "cohere": COHERE_AVAILABLE,
            "watsonx": WATSONX_AVAILABLE,
            "llama-cpp": LLAMA_CPP_AVAILABLE,
            "ollama": True,  # Ollama is always available (HTTP-based)
        }
        return availability_map.get(provider.lower(), False)

    def is_vector_db_available(self, db_type: str) -> bool:
        """Check if a specific vector database is available."""
        availability_map = {
            "db2": DB2_AVAILABLE,
            "inmemory": True,  # In-memory is always available
        }
        return availability_map.get(db_type.lower(), False)

    def get_available_providers(self) -> list[str]:
        """Get list of available LLM providers."""
        providers = ["ollama"]  # Ollama is always available
        if OPENAI_AVAILABLE:
            providers.append("openai")
        if ANTHROPIC_AVAILABLE:
            providers.append("anthropic")
        if COHERE_AVAILABLE:
            providers.append("cohere")
        if WATSONX_AVAILABLE:
            providers.append("watsonx")
        if LLAMA_CPP_AVAILABLE:
            providers.append("llama-cpp")
        return providers

    def get_available_vector_dbs(self) -> list[str]:
        """Get list of available vector databases."""
        dbs = ["inmemory"]  # In-memory is always available
        if DB2_AVAILABLE:
            dbs.append("db2")
        return dbs


@lru_cache
def get_settings() -> Settings:
    """Return a cached application settings instance."""
    return Settings()

# Made with Bob
