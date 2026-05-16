# IBM Dexter AI Code Reviewer - Backend

FastAPI-based backend for AI-powered code review with multi-agent architecture.

## Quick Start

### Prerequisites
- Python 3.9+
- Ollama installed locally (for LLM support)
- Git

### Installation Options

#### Option 1: Minimal Install (Recommended - 2-3 minutes)
Perfect for development and testing with Ollama:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**What's included:**
- ✅ FastAPI web framework
- ✅ SQLAlchemy + SQLite database
- ✅ LangChain core
- ✅ Ollama integration (lightweight)
- ✅ GitHub/GitLab integration
- ✅ ChromaDB vector store
- ✅ Authentication & security
- ✅ ~50 packages, ~2-3 minutes install time

#### Option 2: Full Install (All features - 25+ minutes)
Includes all LLM providers and optional features:

```bash
pip install -r requirements-full.txt
```

**Additional features:**
- All LLM providers (OpenAI, Anthropic, Cohere, Watsonx)
- All vector databases (Db2, Qdrant, Weaviate)
- llama-cpp-python (local models)
- Background tasks (Celery, Redis)
- Testing and development tools
- ~200+ packages, ~25-30 minutes install time

#### Option 3: Custom Install
Install only what you need:

```bash
# Start with minimal
pip install -r requirements.txt

# Add specific features as needed
pip install openai              # OpenAI support
pip install anthropic           # Claude support
pip install langchain-db2       # IBM Db2 vector store
pip install celery redis        # Background tasks
pip install pytest pytest-cov   # Testing tools
```

See `requirements-optional.txt` for all available optional packages.

### Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and configure:
```bash
# Database
DATABASE_URL=sqlite:///./dexter.db

# Ollama (local LLM)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# GitHub Integration
GITHUB_TOKEN=your_github_token_here

# GitLab Integration (optional)
GITLAB_TOKEN=your_gitlab_token_here
GITLAB_URL=https://gitlab.com

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Database Setup

Initialize the database:
```bash
alembic upgrade head
```

### Running the Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## Architecture

### Multi-Agent System

IBM Dexter uses specialized AI agents for different aspects of code review:

- **Security Agent**: Identifies security vulnerabilities and best practices
- **Architecture Agent**: Reviews design patterns and code structure
- **Compliance Agent**: Checks coding standards and guidelines
- **Governance Agent**: Ensures policy compliance
- **Infrastructure Agent**: Reviews deployment and infrastructure code
- **Modernization Agent**: Suggests improvements and refactoring

### RAG Pipeline

Retrieval-Augmented Generation for context-aware reviews:
- Vector store for code embeddings (ChromaDB or IBM Db2)
- Semantic search for relevant code patterns
- Historical review context

### LLM Support

Flexible LLM provider support:
- **Ollama** (default): Local, private, no API costs
- **OpenAI**: GPT-3.5, GPT-4 (optional)
- **Anthropic**: Claude (optional)
- **IBM Watsonx**: Enterprise AI (optional)
- **Cohere**: Command models (optional)

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get token

### Repositories
- `GET /api/v1/repositories` - List repositories
- `POST /api/v1/repositories` - Add repository
- `GET /api/v1/repositories/{id}` - Get repository details

### Pull Requests
- `GET /api/v1/pull-requests` - List pull requests
- `POST /api/v1/pull-requests/{id}/review` - Trigger AI review

### Reviews
- `GET /api/v1/reviews` - List reviews
- `GET /api/v1/reviews/{id}` - Get review details

### Webhooks
- `POST /api/v1/webhooks/github` - GitHub webhook handler
- `POST /api/v1/webhooks/gitlab` - GitLab webhook handler

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest

# With coverage
pytest --cov=app --cov-report=html
```

### Code Quality

```bash
# Install dev tools
pip install black ruff mypy

# Format code
black .

# Lint code
ruff check .

# Type checking
mypy app/
```

## Troubleshooting

### Slow Installation?
- Use `requirements.txt` (minimal) instead of `requirements-full.txt`
- Install optional packages only when needed
- Consider using a package cache or mirror

### Ollama Connection Issues?
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve

# Pull a model
ollama pull llama2
```

### Database Issues?
```bash
# Reset database
rm dexter.db
alembic upgrade head
```

## Production Deployment

### Using Docker

```bash
docker build -t dexter-backend .
docker run -p 8000:8000 dexter-backend
```

### Environment Variables

Set these in production:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Strong random key
- `OLLAMA_BASE_URL`: Ollama server URL
- `GITHUB_TOKEN`: GitHub API token
- `CORS_ORIGINS`: Allowed frontend origins

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions:
- GitHub Issues: [Your Repo URL]
- Documentation: [Your Docs URL]