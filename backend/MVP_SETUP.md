# IBM Dexter MVP Setup - 10 Minutes ⚡

Get your AI-powered PR review bot running in under 10 minutes!

## Prerequisites ✅

Before starting, ensure you have:
- ✅ Python 3.9+ installed
- ✅ Ollama installed with llama3 model
- ✅ GitHub account with admin access to a repository
- ✅ Git installed

### Quick Ollama Setup (if not installed)
```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Pull Llama 3 model
ollama pull llama3

# Verify installation
ollama list
```

---

## Step 1: Install Dependencies (2 min) 📦

```bash
# Navigate to backend directory
cd backend

# Install MVP dependencies
pip install -r requirements-mvp.txt

# Verify installation
python -c "import fastapi, ollama, langchain_db2; print('✅ All dependencies installed!')"
```

---

## Step 2: Configure Environment (2 min) ⚙️

```bash
# Copy example environment file
cp .env.example .env

# Edit configuration
nano .env
```

Add these essential settings:

```bash
# ============================================================================
# MVP CONFIGURATION
# ============================================================================

# GitHub Integration
DEXTER_GITHUB_TOKEN=ghp_your_github_personal_access_token_here
DEXTER_GITHUB_WEBHOOK_SECRET=your_webhook_secret_here

# AI Configuration
DEXTER_OLLAMA_MODEL=llama3
DEXTER_OLLAMA_BASE_URL=http://localhost:11434

# Vector Database (IBM Db2 via langchain-db2)
DEXTER_VECTOR_DB_TYPE=db2
DEXTER_DB2_DATABASE=TESTDB
DEXTER_DB2_HOSTNAME=your-db2-host
DEXTER_DB2_PORT=50000
DEXTER_DB2_UID=your_user
DEXTER_DB2_PWD=your_password
DEXTER_DB2_SCHEMA=DEXTER

# Database
DEXTER_DATABASE_URL=sqlite:///./dexter.db

# API Configuration
DEXTER_API_HOST=0.0.0.0
DEXTER_API_PORT=8000

# Security (generate with: openssl rand -hex 32)
DEXTER_SECRET_KEY=your_secret_key_here
```

### Generate GitHub Token
1. Go to GitHub Settings → Developer Settings → Personal Access Tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo`, `write:discussion`
4. Copy token and add to `.env`

---

## Step 3: Setup GitHub App (3 min) 🤖

### Create GitHub App
1. Go to GitHub Settings → Developer Settings → GitHub Apps
2. Click **"New GitHub App"**

### Configure App Settings

**Basic Information:**
- **GitHub App name**: `Dexter AI Reviewer`
- **Homepage URL**: `https://github.com/your-org/dexter`
- **Webhook URL**: `http://your-server:8000/api/v1/webhooks/github`
  - For local testing: Use ngrok or similar tunnel
- **Webhook secret**: Generate random string (save to `.env`)

**Permissions:**
- Repository permissions:
  - **Pull requests**: Read & Write
  - **Contents**: Read
  - **Metadata**: Read

**Subscribe to events:**
- ✅ Pull request
- ✅ Pull request review
- ✅ Pull request review comment

### Install App
1. After creating, click "Install App"
2. Select repositories to monitor
3. Download private key (save as `github-app-key.pem`)

### Update .env with App Details
```bash
DEXTER_GITHUB_APP_ID=123456
DEXTER_GITHUB_APP_PRIVATE_KEY_PATH=./github-app-key.pem
DEXTER_GITHUB_INSTALLATION_ID=78910
```

---

## Step 4: Add Company Docs (2 min) 📚

```bash
# Create directory for company documentation
mkdir -p data/company_docs

# Add your architecture docs, coding standards, etc.
cp /path/to/your/docs/*.md data/company_docs/

# Example: Create a sample architecture doc
cat > data/company_docs/architecture.md << 'EOF'
# Company Architecture Guidelines

## Microservices Pattern
- Use REST APIs for service communication
- Implement circuit breakers
- Use async/await for I/O operations

## Security Standards
- Always validate input
- Use parameterized queries
- Implement rate limiting

## Code Quality
- Write unit tests (>80% coverage)
- Use type hints
- Follow PEP 8 style guide
EOF

# Ingest documents into vector database
python -c "
from app.rag.vector_store_factory import VectorStoreFactory
from pathlib import Path

# Initialize vector store
store = VectorStoreFactory.create_vector_store()

# Load and ingest documents
docs_path = Path('data/company_docs')
for doc_file in docs_path.glob('*.md'):
    with open(doc_file, 'r') as f:
        content = f.read()
        store.add_documents([{
            'content': content,
            'metadata': {'source': doc_file.name}
        }])

print('✅ Documents ingested successfully!')
"
```

---

## Step 5: Start Server (1 min) 🚀

```bash
# Start the Dexter server
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# You should see:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete.
```

### Verify Server is Running
```bash
# In another terminal
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","version":"1.0.0"}
```

---

## Step 6: Test on PR ✨

### Create Test PR
1. Go to your GitHub repository
2. Create a new branch with some code changes
3. Open a Pull Request
4. Wait for Dexter to comment (usually < 30 seconds)

### Expected Dexter Comment Format
```markdown
## 🤖 Dexter AI Review

### Summary
Analyzed 5 files with 234 lines of code. Found 2 suggestions for improvement.

### Findings

#### 🟡 Suggestions (2)
1. **Line 45 in `src/api.py`**: Consider using async/await for better performance
   ```python
   # Current
   def fetch_data():
       return requests.get(url)
   
   # Suggested
   async def fetch_data():
       async with httpx.AsyncClient() as client:
           return await client.get(url)
   ```

2. **Line 67 in `src/utils.py`**: Add error handling for edge cases
   ```python
   # Add try-except block
   try:
       result = process_data(input)
   except ValueError as e:
       logger.error(f"Invalid input: {e}")
       return None
   ```

### Company Knowledge
✅ This change aligns with our microservices architecture pattern.
⚠️ Consider adding unit tests to meet our 80% coverage requirement.

---
*Powered by IBM Watsonx & Ollama | Reviewed in 2.3s*
```

---

## Done! 🎉

Your Dexter bot is now reviewing PRs automatically!

---

## Troubleshooting 🔧

### Issue: "Ollama connection refused"
```bash
# Start Ollama service
ollama serve

# Verify it's running
curl http://localhost:11434/api/tags
```

### Issue: "GitHub webhook not receiving events"
```bash
# For local development, use ngrok
ngrok http 8000

# Update webhook URL in GitHub App settings to ngrok URL
# Example: https://abc123.ngrok.io/api/v1/webhooks/github
```

### Issue: "Vector store not found"
```bash
# Verify Db2 connectivity and re-initialize the vector store. db2vs will
# auto-create the required tables on first use.
python -c "from app.rag.vector_store_factory import VectorStoreFactory; VectorStoreFactory.create_vector_store()"
```

### Issue: "Import errors"
```bash
# Reinstall dependencies
pip install --upgrade -r requirements-mvp.txt

# Verify Python version
python --version  # Should be 3.9+
```

---

## Next Steps 🚀

1. **Add More Company Docs**: Expand your knowledge base
   ```bash
   cp more-docs/*.md data/company_docs/
   python scripts/ingest_docs.py
   ```

2. **Customize AI Prompts**: Edit `app/services/ai_service.py`
   - Adjust review tone
   - Add specific checks
   - Customize output format

3. **Monitor Performance**: Check logs
   ```bash
   tail -f logs/dexter.log
   ```

4. **Deploy to Production**: Use Docker
   ```bash
   docker build -t dexter-bot .
   docker run -p 8000:8000 dexter-bot
   ```

5. **Add More Repositories**: Install GitHub App on more repos

---

## Configuration Reference 📖

### Minimal .env for MVP
```bash
# Required
DEXTER_GITHUB_TOKEN=ghp_xxx
DEXTER_OLLAMA_MODEL=llama3
DEXTER_VECTOR_DB_TYPE=db2
DEXTER_DB2_DATABASE=TESTDB
DEXTER_DB2_HOSTNAME=your-db2-host
DEXTER_DB2_UID=your_user
DEXTER_DB2_PWD=your_password

# Optional (has defaults)
DEXTER_API_PORT=8000
DEXTER_DATABASE_URL=sqlite:///./dexter.db
DEXTER_DB2_SCHEMA=DEXTER
DEXTER_DB2_TABLE_PREFIX=DEXTER
```

### Advanced Configuration
See `backend/.env.example` for all available options.

---

## Support 💬

- **Documentation**: See `MVP_FEATURES.md` for feature details
- **Issues**: Check `TESTING.md` for common problems
- **Architecture**: Review `docs/architecture/` for system design

---

## Quick Commands Cheat Sheet 📝

```bash
# Start server
python3 -m uvicorn main:app --reload

# Check health
curl http://localhost:8000/health

# View logs
tail -f logs/dexter.log

# Reingest docs
python scripts/ingest_docs.py

# Run tests
pytest

# Stop server
Ctrl+C
```

---

**Congratulations! You now have a working AI PR review bot! 🎊**