# Deploy IBM Dexter (hackathon / MVP)

The app is a **monorepo**: Python **FastAPI** backend under `backend/`, **Vite + React** frontend under `frontend/`. Deploy them as **two services** and connect the UI to the API with **`VITE_API_URL`**.

## Frontend ↔ backend

1. Deploy the backend first and note its **HTTPS origin** (no path), e.g. `https://dexter-api.up.railway.app`.
2. The SPA must call the API at **`{origin}/api/v1`**. Set at **build time**:

   ```bash
   # example
   export VITE_API_URL=https://dexter-api.up.railway.app/api/v1
   cd frontend && npm ci && npm run build
   ```

3. Backend **CORS** must allow your frontend origin:

   ```bash
   DEXTER_CORS_ORIGINS=https://your-frontend.vercel.app
   ```

   Multiple origins: comma-separated, no spaces (or match how `Settings.cors_origins` splits).

4. **Hackathon MVP**: `DEXTER_REQUIRE_API_BEARER_AUTH=false` (default) keeps the API open. For production later, set strong `DEXTER_JWT_SECRET_KEY`, `DEXTER_API_KEY`, webhook secrets, and enable auth as documented in `backend/.env.example`.

## Railway (recommended quick path)

**Backend**

1. New project → Deploy from GitHub → select this repo.
2. **Root Directory**: `backend`.
3. **Start Command** (if not using `railway.toml`):
   `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. **Variables**: copy from `backend/.env.example` (use **Variables** tab, not committed `.env`).
5. For `DEXTER_APP_ENV=production`, you must set **non-default** `DEXTER_JWT_SECRET_KEY`, `DEXTER_API_KEY`, and webhook secrets or the app will refuse to start (`assert_deployment_safe`). For demos use `DEXTER_APP_ENV=development` unless you have real secrets.

### 🤖 Configure LLM Provider (REQUIRED for Production)

**⚠️ CRITICAL:** Ollama only works locally. For Railway production, you **MUST** configure a cloud LLM provider or you'll see "No available LLM providers found" errors.

**Quick Setup (OpenAI - Recommended):**
1. Get API key: https://platform.openai.com/api-keys
2. Add to Railway Variables:
   ```bash
   DEXTER_OPENAI_API_KEY=sk-...your-key...
   DEXTER_LLM_PROVIDER=openai
   DEXTER_DEFAULT_LLM_PROVIDER=openai
   DEXTER_OPENAI_MODEL=gpt-4o-mini
   ```
3. Railway will auto-redeploy

**See `PRODUCTION_LLM_SETUP.md` for:**
- Detailed setup instructions for OpenAI, Watsonx, and Anthropic
- Cost estimates and provider comparison
- Troubleshooting guide
- Understanding Railway logs

**Frontend**

1. New service (static or Node build) → same repo, **Root Directory**: `frontend`.
2. **Build**: `npm ci && npm run build`.
3. **Publish directory**: `dist`.
4. **Build variable**: `VITE_API_URL=https://<your-backend>.up.railway.app/api/v1`.

## Render

- Use `backend/render.yaml` as a starting point, or create a **Web Service** with root `backend`, build `pip install -r requirements.txt`, start `uvicorn main:app --host 0.0.0.0 --port $PORT`.
- Frontend: **Static Site**, root `frontend`, build `npm run build`, publish `dist`, set env `VITE_API_URL` in build env.

## Netlify / Vercel (frontend)

- **`frontend/netlify.toml`** and **`frontend/vercel.json`** configure SPA fallback so React Router works.
- Set **`VITE_API_URL`** in the host’s environment (Netlify: site env; Vercel: project env) before build.
- See **`frontend/.env.production.example`**.

## Replit

- **`.replit`** runs the backend from `backend/`. Add **Secrets** for `.env`-style keys.
- Host the frontend on Netlify/Vercel, or a second Repl, with `VITE_API_URL` pointing at this Repl’s public URL + `/api/v1`.

## Local sanity check

```bash
cd backend && pip install -r requirements.txt && uvicorn main:app --reload --port 8000
cd frontend && npm ci && npm run dev
# Vite proxies /api to :8000 in dev; production relies on VITE_API_URL.
```

## Branch note

The branch **`demo/main-snapshot`** points at the last **`origin/main`** commit before the product-ready push, if you need the previous demo baseline.
