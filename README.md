# IBM Dexter — AI Code Reviewer

**Enterprise intelligence for code review** — multi-agent analysis, knowledge-base (RAG), GitHub/GitLab hooks, and a manager-ready dashboard built on **IBM Carbon Design System**.

> **Built entirely with IBM Bob** — every feature, interface, test, and deployment artifact in this repository was created using **IBM Bob** as the development assistant. Custom **Bob skills** (see `skills/` and `.bob/`) were authored to standardize patterns, accelerate delivery, and keep quality high across frontend, backend, and tests.

---

## Why enterprises care

| Need | How Dexter helps |
|------|-------------------|
| **Engineering productivity** | Faster, consistent PR reviews with specialized agents (security, architecture, compliance, modernization, performance). |
| **Visibility for managers** | Dashboard, review history, and analytics-oriented pages so leads can see throughput, severity trends, and team engagement with AI-assisted review. |
| **Governance & context** | Knowledge base + optional **IBM Db2** vector integration for org standards, policies, and internal docs in the review loop. |
| **Flexible AI** | **IBM watsonx**, OpenAI, Ollama, Anthropic, Cohere — configure what your compliance and procurement allow. |

Dexter is designed to sit beside your existing Git workflows (webhooks, token-based API access) without replacing your source of truth.

---

## IBM Bob & custom skills

This project is intentionally **Bob-native**:

- **Assistant:** All application code, configuration, tests, and docs were produced **with IBM Bob only** — a deliberate choice for speed, consistency, and repeatability inside IBM-aligned teams.
- **Skills:** The `skills/` directory contains modular **Bob skill** definitions (Carbon UI, multi-agent pipelines, RAG, testing, PDF/export, Bob integration). They encode conventions so Bob stays on rails across sessions and contributors.
- **Auto-loader:** `.bob/config/` hosts the skill loader configuration (`skill-loader.json`) and `auto-loader.py` to analyze prompts, suggest skills, and track usage.

Using Bob + these skills materially **boosts team productivity**: less time on boilerplate, fewer mismatched patterns between React and FastAPI, and faster iteration on new agents or UI surfaces.

```bash
# Example: inspect Bob skill tooling (from repo root)
python .bob/config/auto-loader.py list
python .bob/config/auto-loader.py analyze "add RAG search to knowledge base"
```

---

## Architecture (high level)

| Layer | Stack |
|--------|--------|
| **Frontend** | **Vite**, **React 18**, **IBM Carbon**, **TanStack Query**, **React Router** — `frontend/` |
| **Backend** | **FastAPI**, **SQLAlchemy**, **LangChain** (0.3.x), optional **IBM Db2** via `langchain-db2` — `backend/` |
| **AI** | Pluggable LLM providers; embeddings for RAG; multi-agent orchestration in services and agents |
| **Hosting** | **Monorepo**: deploy API and SPA separately — see **`DEPLOY.md`** (Railway, Render, Replit, Netlify, Vercel) |

```
IBM_Dexter/
├── backend/                 # FastAPI app (uvicorn main:app)
│   ├── app/
│   │   ├── api/v1/endpoints/
│   │   ├── agents/
│   │   ├── services/
│   │   └── tests/           # pytest suite (API, LLM stubs, settings, embeddings)
│   ├── main.py
│   ├── requirements.txt
│   ├── Procfile             # PaaS process entry
│   └── railway.toml         # Example Railway config
├── frontend/                # Vite + React + Carbon
│   ├── src/
│   ├── netlify.toml
│   └── vercel.json
├── .bob/config/             # Bob auto-loader & skill mapping
├── skills/                  # Bob skill modules (core, integration, testing)
├── DEPLOY.md                # Production / hackathon deployment guide
└── README.md                # This file
```

---

## Quick start (local)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # Edit: LLM, DB, CORS, optional auth
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Health check: `GET http://localhost:8000/health`  
API base: `http://localhost:8000/api/v1`

### Frontend

```bash
cd frontend
npm ci
npm run dev                # http://localhost:3000 — Vite proxies /api to :8000 in dev
```

For production builds, set **`VITE_API_URL`** to your public API (e.g. `https://api.example.com/api/v1`). See `frontend/.env.production.example`.

---

## Testing & quality

Quality is a first-class concern; tests were written and maintained **with IBM Bob** alongside product code.

### Backend (pytest)

```bash
cd backend
pip install -r requirements-dev.txt   # pytest, pytest-asyncio, pytest-cov, respx
pytest app/tests/ -v                  # API, auth flow, webhooks, settings, embeddings, OpenAI HTTP stubs
```

Included tests (under `backend/app/tests/`):

- **`test_api.py`** — health, auth (register/login/refresh), repository CRUD, PR review flow, webhooks, optional JWT/API-key protection
- **`test_effective_ai_config.py`** — resolved LLM / embedding / deployment hints
- **`test_embeddings_service.py`** — embedding provider behavior
- **`test_openai_llm_http.py`** — OpenAI chat LLM HTTP path
- **`test_settings_ai_payload.py`** — settings payload shape for the UI  
Shared fixtures and env defaults live in **`conftest.py`**.

### Frontend

```bash
cd frontend
npm run test              # Vitest
npm run lint
```

---

## Configuration highlights

Copy **`backend/.env.example`** → **`.env`** and set:

- **`DEXTER_LLM_PROVIDER`** — e.g. `watsonx`, `openai`, `ollama`
- **`DEXTER_CORS_ORIGINS`** — your frontend origin(s), comma-separated
- **Secrets** — provider API keys, Db2, GitHub/GitLab tokens as needed
- **`DEXTER_REQUIRE_API_BEARER_AUTH`** — default `false` for hackathon/MVP; set `true` when you want JWT / `X-API-Key` on data routes

Production safety: if **`DEXTER_APP_ENV`** is `staging` or `production`, the app **refuses to start** with default example secrets (JWT, API key, webhook secrets) until you replace them.

---

## Deployment

See **`DEPLOY.md`** for:

- Split deploy (backend + frontend)
- **`VITE_API_URL`** and CORS alignment
- Railway, Render, Replit, Netlify, Vercele

---

## Demos & branches

- **`main`** — current product-ready line (hosting configs, tests, Bob skills in-repo).
- **`demo/main-snapshot`** — frozen snapshot of `main` before the latest product-ready push, useful for fixed hackathon demos.

---

## Roadmap (informal)

- Harden auth with a persistent user store (today: optional JWT; in-memory users for auth endpoints when enabled).
- Deeper manager analytics and exports (PDF/report skills already sketched in `skills/`).
- Broader IdP / SSO for enterprise rollouts.

---

## Acknowledgments

- **IBM Bob** — end-to-end assisted development for this codebase.
- **IBM Carbon** — design system and React components.
- **LangChain**, **FastAPI**, and the **open-source** communities behind the backend and tooling.

---

**IBM Dexter** — *enterprise-grade AI code review, built with IBM Bob, skills, and tests you can run today.*

<!-- Made with Bob -->
