# IBM Dexter - Quick Installation Guide

## 🚀 Quick Start (2-3 Minutes)

This guide will get you up and running with IBM Dexter using Ollama in under 3 minutes.

### Prerequisites

Before you begin, ensure you have:
- ✅ Python 3.9 or higher
- ✅ Ollama installed and running locally
- ✅ Git (for cloning repositories)

### Step 1: Install Ollama

If you haven't installed Ollama yet:

**macOS/Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from [ollama.com](https://ollama.com/download)

**Start Ollama and pull a model:**
```bash
ollama serve  # Start Ollama server
ollama pull llama2  # Or llama3, mistral, codellama, etc.
```

### Step 2: Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd IBM\ Dexter_AI_Code_Reviewer/backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install minimal dependencies (2-3 minutes)
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

**Minimal configuration for Ollama:**
```bash
# Database (SQLite - no setup needed)
DATABASE_URL=sqlite:///./dexter.db

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# GitHub Token (get from https://github.com/settings/tokens)
GITHUB_TOKEN=your_github_token_here

# Security (generate a random string)
SECRET_KEY=your-secret-key-here
```

### Step 4: Initialize Database

```bash
# Create database tables
alembic upgrade head
```

### Step 5: Start the Server

```bash
# Start FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**That's it!** 🎉

Access the API at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

---

## 📦 What's Included in Minimal Install

The minimal installation (`requirements.txt`) includes:

### Core Framework (~20 packages)
- FastAPI + Uvicorn (web server)
- SQLAlchemy + Alembic (database)
- Pydantic (data validation)

### AI & LLM (~15 packages)
- LangChain core (no heavy providers)
- Ollama client (lightweight)
- IBM Db2 vector store (via `langchain-db2`)

### Integrations (~10 packages)
- PyGithub (GitHub API)
- python-gitlab (GitLab API)
- httpx, aiohttp (HTTP clients)

### Security (~5 packages)
- python-jose (JWT tokens)
- passlib (password hashing)

**Total: ~50 packages, ~2-3 minutes install time**

---

## 🔧 Adding Optional Features

You can add features later without reinstalling everything:

### Add OpenAI Support
```bash
pip install openai
```

Then update `.env`:
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

### Add Claude Support
```bash
pip install anthropic
```

Then update `.env`:
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

### Configure IBM Db2 Vector Store

`langchain-db2`, `ibm-db`, and `ibm-db-sa` are installed by default in
`requirements.txt`. Just point Dexter at your Db2 instance via `.env`:

```bash
DEXTER_VECTOR_DB_TYPE=db2
DEXTER_DB2_DATABASE=TESTDB
DEXTER_DB2_HOSTNAME=your-db2-host
DEXTER_DB2_PORT=50000
DEXTER_DB2_UID=your-username
DEXTER_DB2_PWD=your-password
DEXTER_DB2_SCHEMA=DEXTER
```

The `db2vs` component will auto-create the required vector tables on first use.

### Add Background Tasks
```bash
pip install celery redis
```

### Add Testing Tools
```bash
pip install pytest pytest-asyncio pytest-cov
```

---

## 🐳 Docker Installation (Alternative)

If you prefer Docker:

```bash
# Build image
docker build -t dexter-backend .

# Run container
docker run -p 8000:8000 \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  -e GITHUB_TOKEN=your_token \
  dexter-backend
```

---

## 🔍 Troubleshooting

### Installation Taking Too Long?

**Problem:** Installation is taking 25+ minutes

**Solution:** Make sure you're using `requirements.txt` (minimal), not `requirements-full.txt`:
```bash
# Stop current installation (Ctrl+C)
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # NOT requirements-full.txt
```

### Ollama Connection Error

**Problem:** `Connection refused to localhost:11434`

**Solution:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it
ollama serve

# Pull a model if needed
ollama pull llama2
```

### Database Errors

**Problem:** Database tables don't exist

**Solution:**
```bash
# Reset and recreate database
rm dexter.db
alembic upgrade head
```

### Import Errors for Optional Packages

**Problem:** `ModuleNotFoundError: No module named 'openai'`

**Solution:** This is expected if you haven't installed optional packages. Either:
1. Install the package: `pip install openai`
2. Or use Ollama instead: Set `LLM_PROVIDER=ollama` in `.env`

The application gracefully handles missing optional packages.

---

## 📊 Installation Comparison

| Feature | Minimal Install | Full Install |
|---------|----------------|--------------|
| **Time** | 2-3 minutes | 25-30 minutes |
| **Packages** | ~50 | ~200+ |
| **Size** | ~200 MB | ~2+ GB |
| **LLM Support** | Ollama only | All providers |
| **Vector DB** | IBM Db2 (`langchain-db2`) | IBM Db2 (`langchain-db2`) |
| **Use Case** | Development, Testing | Production, All features |

---

## 🎯 Recommended Setup

### For Development & Testing
```bash
pip install -r requirements.txt
```
- Fast installation
- Ollama for local LLM
- IBM Db2 for vectors (via `langchain-db2`)
- SQLite for database
- Perfect for learning and testing

### For Production
```bash
pip install -r requirements-full.txt
```
- All LLM providers
- All vector databases
- Production-ready features
- Background tasks
- Monitoring tools

### For Specific Use Cases
```bash
# Start minimal
pip install -r requirements.txt

# Add only what you need
pip install openai  # If using OpenAI
pip install langchain-db2  # If using Db2
pip install celery redis  # If using background tasks
```

---

## 📚 Next Steps

After installation:

1. **Configure GitHub Integration**
   - Create a GitHub token: https://github.com/settings/tokens
   - Add to `.env`: `GITHUB_TOKEN=your_token`

2. **Test the API**
   - Visit http://localhost:8000/docs
   - Try the `/health` endpoint
   - Register a user account

3. **Connect a Repository**
   - Use the API to add a repository
   - Trigger a code review
   - View results in the dashboard

4. **Explore Features**
   - Multi-agent AI reviews
   - RAG-based context
   - GitHub/GitLab webhooks
   - Historical analytics

---

## 🆘 Getting Help

- **Documentation**: See `backend/README.md`
- **API Docs**: http://localhost:8000/docs
- **Issues**: [GitHub Issues]
- **Discussions**: [GitHub Discussions]

---

## 📝 Summary

**Minimal Install (Recommended):**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
alembic upgrade head
uvicorn main:app --reload
```

**Access:** http://localhost:8000/docs

**Time:** 2-3 minutes ⚡

Happy coding! 🚀