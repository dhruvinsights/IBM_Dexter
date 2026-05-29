# IBM Dexter AI Code Reviewer

AI-powered code review platform with multi-agent architecture for comprehensive code analysis.

## 🚀 Quick Links

### For Production Deployment (Railway/Cloud)
- **🚨 Quick Fix (5 min):** [`RAILWAY_QUICK_FIX.md`](RAILWAY_QUICK_FIX.md) - Fix "No LLM providers found" error
- **📚 Complete Guide:** [`PRODUCTION_LLM_SETUP.md`](PRODUCTION_LLM_SETUP.md) - Full LLM provider setup
- **🚢 Deployment:** [`DEPLOY.md`](DEPLOY.md) - Deploy to Railway, Render, Vercel, Netlify

### For Local Development
- **Backend Setup:** [`backend/README.md`](backend/README.md)
- **Frontend Setup:** [`frontend/README.md`](frontend/README.md)

## 🎯 Current Production Status

If you're seeing "No available LLM providers found" errors:

✅ **Your frontend IS connected** - The connection is working
✅ **Your backend IS running** - The server is operational
✅ **GitHub IS configured** - Your token is working
❌ **LLM Provider needed** - Ollama doesn't work in cloud

**Solution:** Add OpenAI API key to Railway (5 minutes)
👉 See [`RAILWAY_QUICK_FIX.md`](RAILWAY_QUICK_FIX.md)

## 📋 Project Structure

```
IBM Dexter/
├── backend/              # FastAPI backend
│   ├── app/             # Application code
│   │   ├── agents/      # AI agents (security, architecture, etc.)
│   │   ├── api/         # REST API endpoints
│   │   ├── models/      # Database models
│   │   ├── services/    # Business logic
│   │   └── rag/         # RAG & vector stores
│   └── README.md        # Backend documentation
├── frontend/            # React + Vite frontend
│   ├── src/            # Source code
│   └── README.md       # Frontend documentation
└── docs/               # Additional documentation
```

## 🤖 Features

- **Multi-Agent AI Review:** Security, Architecture, Compliance, Infrastructure agents
- **GitHub/GitLab Integration:** Automatic PR reviews
- **RAG Knowledge Base:** Context-aware code analysis
- **IBM Ecosystem:** Watsonx, Db2 vector store support
- **Real-time Dashboard:** Live metrics and insights
- **Governance Policies:** Customizable review rules

## 🛠️ Technology Stack

### Backend
- **Framework:** FastAPI (Python 3.9+)
- **Database:** PostgreSQL (production), SQLite (development)
- **LLM Providers:** OpenAI, IBM Watsonx, Anthropic, Ollama (local)
- **Vector Stores:** IBM Db2, Qdrant, Weaviate
- **AI Framework:** LangChain

### Frontend
- **Framework:** React 18 + Vite
- **UI Library:** IBM Carbon Design System
- **State Management:** Zustand
- **Charts:** Carbon Charts
- **Styling:** SCSS

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd IBM-Dexter
   ```

2. **Start Backend**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your settings
   uvicorn main:app --reload
   ```

3. **Start Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Access Application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Production Deployment

See [`DEPLOY.md`](DEPLOY.md) for detailed deployment instructions for:
- Railway (recommended)
- Render
- Vercel/Netlify (frontend)
- Replit

**Important:** Configure a cloud LLM provider for production (see [`PRODUCTION_LLM_SETUP.md`](PRODUCTION_LLM_SETUP.md))

## 📖 Documentation

- [`PRODUCTION_LLM_SETUP.md`](PRODUCTION_LLM_SETUP.md) - LLM provider configuration
- [`RAILWAY_QUICK_FIX.md`](RAILWAY_QUICK_FIX.md) - Quick production fix
- [`DEPLOY.md`](DEPLOY.md) - Deployment guide
- [`backend/README.md`](backend/README.md) - Backend documentation
- [`frontend/README.md`](frontend/README.md) - Frontend documentation
- [`docs/`](docs/) - Architecture and planning docs

## 🔧 Configuration

### Environment Variables

**Backend (`.env`):**
```bash
# LLM Provider (choose one)
DEXTER_OPENAI_API_KEY=sk-...
DEXTER_WATSONX_API_KEY=...
DEXTER_ANTHROPIC_API_KEY=sk-ant-...

# Database
DATABASE_URL=postgresql://...

# Security
DEXTER_SECRET_KEY=...
DEXTER_JWT_SECRET=...

# GitHub Integration
DEXTER_GITHUB_TOKEN=ghp_...
```

**Frontend (`.env`):**
```bash
VITE_API_URL=http://localhost:8000/api/v1
```

See `.env.example` files for complete configuration options.

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📊 Monitoring

- **Backend Logs:** Check Railway/Render logs
- **Frontend:** Browser console
- **API Health:** `GET /api/v1/health`
- **LLM Status:** `GET /api/v1/settings/ollama/health`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

[Add your license here]

## 🆘 Support

- **Production Issues:** See [`RAILWAY_QUICK_FIX.md`](RAILWAY_QUICK_FIX.md)
- **LLM Setup:** See [`PRODUCTION_LLM_SETUP.md`](PRODUCTION_LLM_SETUP.md)
- **General Questions:** Check documentation in `docs/`

## 🎯 Roadmap

See [`IBM_DEXTER_MVP_ROADMAP.md`](IBM_DEXTER_MVP_ROADMAP.md) for planned features and enhancements.
