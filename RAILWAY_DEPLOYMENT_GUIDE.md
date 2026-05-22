# 🚂 Railway Deployment Guide for IBM Dexter Backend

This guide will help you deploy the IBM Dexter backend to Railway with PostgreSQL database support.

---

## 📋 Table of Contents

1. [Railway Project Setup](#1-railway-project-setup)
2. [Environment Variables Configuration](#2-environment-variables-configuration)
3. [Configuring Credentials via Settings UI](#3-configuring-credentials-via-settings-ui)
4. [Railway-Specific Settings](#4-railway-specific-settings)
5. [Database Setup](#5-database-setup)
6. [Post-Deployment Steps](#6-post-deployment-steps)
7. [Testing Checklist](#7-testing-checklist)
8. [Quick Copy-Paste Configuration](#8-quick-copy-paste-configuration)
9. [Why UI-Based Configuration?](#9-why-ui-based-configuration)
10. [Troubleshooting](#10-troubleshooting)

---


## 📸 Railway Configuration Screenshots Guide

### Critical Settings Checklist

Before deploying, ensure these settings are configured in Railway Dashboard:

#### ✅ Root Directory Configuration
**Location:** Project → Service → Settings → Root Directory

**Setting:**
```
Root Directory: backend
```

**Why it matters:** Railway needs to know your application is in the `/backend` subdirectory, not the root directory. Without this, Railway will look for `start.sh` and other files in the wrong location.

#### ✅ Build Command Configuration
**Location:** Project → Service → Settings → Build Command

**Setting:**
```
Build Command: pip install -r requirements.txt
```

**Why it matters:** Tells Railway how to install your Python dependencies.

#### ✅ Start Command Configuration
**Location:** Project → Service → Settings → Start Command

**Setting:**
```
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Why it matters:** Tells Railway how to start your FastAPI application. The `$PORT` variable is automatically provided by Railway.

#### ✅ Environment Variables
**Location:** Project → Service → Variables

**Required Variables:**
- `DEXTER_SECRET_KEY` - Generate with: `openssl rand -hex 32`
- `DEXTER_JWT_SECRET` - Generate with: `openssl rand -hex 32`
- `DEXTER_FRONTEND_URL` - Your frontend URL (e.g., `https://ibm-dexter.vercel.app`)
- `DEXTER_CORS_ORIGINS` - Same as frontend URL
- `DATABASE_URL` - Auto-injected by Railway when you add PostgreSQL

### Step-by-Step Configuration Process

1. **Create New Project in Railway**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your IBM Dexter repository

2. **Add PostgreSQL Database**
   - Click "+ New" in your project
   - Select "Database" → "PostgreSQL"
   - Railway automatically links it to your service

3. **Configure Service Settings**
   - Click on your service (not the database)
   - Go to "Settings" tab
   - Set **Root Directory** to `backend`
   - Set **Build Command** to `pip install -r requirements.txt`
   - Set **Start Command** to `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Add Environment Variables**
   - Go to "Variables" tab
   - Click "Raw Editor" for bulk paste
   - Paste the minimal configuration from Section 8
   - Click "Save"

5. **Deploy**
   - Railway will automatically deploy after saving settings
   - Monitor the "Deployments" tab for build progress
   - Check "Logs" for any errors

### Important Settings Summary

| Setting | Value | Location |
|---------|-------|----------|
| **Root Directory** | `backend` | Settings → Root Directory |
| **Build Command** | `pip install -r requirements.txt` | Settings → Build Command |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` | Settings → Start Command |
| **Python Version** | 3.10 or higher | Auto-detected by Nixpacks |
| **Health Check Path** | `/health` | Settings → Health Check |

### Verification Steps

After configuration, verify in Railway Dashboard:

- [ ] **Root Directory** shows `backend` (not empty or `/`)
- [ ] **Build Command** is set correctly
- [ ] **Start Command** includes `$PORT` variable
- [ ] **PostgreSQL** database is added and linked
- [ ] **Environment Variables** include all required keys
- [ ] **Deployment** shows "Success" status
- [ ] **Logs** show "Application startup complete"

## 1. Railway Project Setup

### Step 1.1: Configure Root Directory
Railway needs to know that your backend is in the `/backend` subdirectory.

**In Railway Dashboard:**
1. Go to your project → **Settings**
2. Find **Root Directory** setting
3. Set to: `/backend`
4. Click **Save**

### Step 1.2: Configure Build & Start Commands

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

> ⚠️ **Important:** Railway automatically provides the `$PORT` environment variable. Your app must use it.

### Step 1.3: Add PostgreSQL Database

1. In Railway Dashboard, click **+ New**
2. Select **Database** → **PostgreSQL**
3. Railway will automatically:
   - Create a PostgreSQL instance
   - Generate `DATABASE_URL` environment variable
   - Link it to your backend service

---

## 2. Environment Variables Configuration

## 🎯 Important: Minimal Configuration Approach

IBM Dexter uses a **Settings UI** for credential management. Most configuration (GitHub tokens, LLM API keys, etc.) should be entered through the web interface at `/settings`, NOT hardcoded in environment variables.

**Why this approach?**
- ✅ Users can update credentials without redeploying
- ✅ Multiple users can have different credentials
- ✅ Credentials are stored securely in the database
- ✅ No need to expose secrets in Railway dashboard
- ✅ More flexible and user-friendly

**Environment variables are ONLY needed for:**
- Application security (JWT secrets)
- Database connection (auto-configured by Railway)
- CORS configuration (frontend URL)
- Basic app settings

---

### 🔑 Generate Required Secrets First

Before configuring Railway, generate these secrets on your local machine:

```bash
# Generate SECRET_KEY (for session management)
openssl rand -hex 32

# Generate JWT_SECRET (for authentication tokens)
openssl rand -hex 32
```

**Save these values!** You'll need them in the next step.

---

### 📝 Minimal Required Environment Variables

Copy these into Railway's environment variables section:

#### **Core Application Settings**
```bash
DEXTER_APP_NAME=IBM Dexter AI Code Reviewer
DEXTER_ENVIRONMENT=production
```

#### **Database Configuration**
```bash
# Railway auto-injects DATABASE_URL for PostgreSQL
DATABASE_URL=${DATABASE_URL}
```

> 💡 **Note:** Railway provides `DATABASE_URL` automatically when you add PostgreSQL. The backend will handle the async conversion internally.

#### **Security & Authentication**
```bash
# Use the secrets you generated above
DEXTER_SECRET_KEY=<PASTE_YOUR_GENERATED_SECRET_KEY>
DEXTER_JWT_SECRET=<PASTE_YOUR_GENERATED_JWT_SECRET>
```

#### **CORS Configuration**
```bash
# CRITICAL: Include your frontend URL
DEXTER_FRONTEND_URL=https://ibm-dexter.vercel.app
DEXTER_CORS_ORIGINS=https://ibm-dexter.vercel.app
```

> ⚠️ **Important:** Update with your actual frontend URL if different.

#### **API Configuration**
```bash
DEXTER_API_HOST=0.0.0.0
DEXTER_API_PORT=8000
```

---

### 🚫 What NOT to Put in Environment Variables

**DO NOT add these to Railway environment variables:**
- ❌ `DEXTER_GITHUB_TOKEN` - Configure in Settings UI
- ❌ `DEXTER_GITHUB_WEBHOOK_SECRET` - Configure in Settings UI
- ❌ `DEXTER_OPENAI_API_KEY` - Configure in Settings UI
- ❌ `DEXTER_WATSONX_*` credentials - Configure in Settings UI
- ❌ `DEXTER_ANTHROPIC_API_KEY` - Configure in Settings UI
- ❌ `DEXTER_LLM_PROVIDER` - User selects in Settings UI
- ❌ Any other user-specific credentials

**These should ALL be configured through the Settings UI after deployment!**

---

## 3. Configuring Credentials via Settings UI

After Railway deployment, configure all credentials through the web interface:

### Step 1: Access Settings
Navigate to: `https://your-backend.railway.app/settings` (or use frontend settings page at `https://ibm-dexter.vercel.app/settings`)

### Step 2: Configure GitHub Integration
- **GitHub Personal Access Token**: Enter your token with `repo` and `webhook` scopes
  - Get from: https://github.com/settings/tokens
  - Required scopes: `repo`, `read:org`, `write:repo_hook`
- **Webhook Secret**: Generate and enter a secure webhook secret
  - Generate with: `openssl rand -hex 32`
- **Repository Access**: Configure which repos to monitor

### Step 3: Configure LLM Provider
Choose your preferred provider and enter credentials:

**Option A: OpenAI (Recommended for Production)**
- **API Key**: Your OpenAI API key (from https://platform.openai.com/api-keys)
- **Model**: `gpt-4o-mini` or `gpt-4` (recommended)
- **Temperature**: `0.7` (default, adjustable)
- **Max Tokens**: `2000` (default)

**Option B: Watsonx (IBM Enterprise)**
- **API Key**: Your IBM Cloud API key
- **Project ID**: Your Watsonx project ID
- **URL**: `https://us-south.ml.cloud.ibm.com` (or your region)
- **Model**: `ibm/granite-13b-chat-v2` or similar

**Option C: Anthropic Claude**
- **API Key**: Your Anthropic API key
- **Model**: `claude-3-opus-20240229` or `claude-3-sonnet-20240229`
- **Temperature**: `0.7` (default)

**Option D: Ollama (Local/Development Only)**
- **Endpoint**: Your Ollama server URL (e.g., `http://localhost:11434`)
- **Model**: `codellama`, `qwen2.5-coder:14b`, etc.
- ⚠️ **Note**: Not recommended for Railway cloud deployment

### Step 4: Configure Embeddings (for Knowledge Base)
- **Provider**: OpenAI (recommended)
- **Model**: `text-embedding-3-small`
- **Dimension**: `1536`

### Step 5: Save and Test
- Click **"Save Settings"**
- Use **"Test Connection"** button to verify each integration
- Check **"Test GitHub Webhook"** to verify webhook setup
- Try a test code review to confirm LLM is working

---

## 4. Railway-Specific Settings

### Service Configuration Summary

| Setting | Value |
|---------|-------|
| **Root Directory** | `/backend` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Health Check Path** | `/health` |
| **Port** | `$PORT` (Railway auto-assigns) |

### Health Check Configuration

Railway will automatically monitor your service health at:
```
https://your-backend.railway.app/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "IBM Dexter Backend",
  "version": "0.1.0"
}
```

---

## 5. Database Setup

### Step 5.1: Add PostgreSQL Service

1. In Railway Dashboard, click **+ New**
2. Select **Database** → **PostgreSQL**
3. Railway automatically creates these variables:
   - `DATABASE_URL`
   - `PGHOST`
   - `PGPORT`
   - `PGUSER`
   - `PGPASSWORD`
   - `PGDATABASE`

### Step 5.2: Database Connection

Railway provides `DATABASE_URL` automatically. The backend application will handle the async conversion internally, so you don't need to manually configure the database URL format.

### Step 5.3: Initialize Database

After deployment, database tables will be created automatically on first run. You can verify by checking Railway logs for successful database initialization.

---

## 6. Post-Deployment Steps

### Step 6.1: Configure Credentials via UI (FIRST!)
**⚠️ Do this BEFORE testing anything else!**

1. Navigate to: `https://your-backend.railway.app/settings`
2. Enter GitHub token, LLM provider credentials
3. Test connections before proceeding
4. Save all settings

### Step 6.2: Get Your Railway Backend URL

After deployment, Railway will provide a URL like:
```
https://ibm-dexter-backend-production.up.railway.app
```

### Step 6.3: Update Frontend Environment Variable

1. Go to your Vercel project: https://vercel.com/dashboard
2. Navigate to **Settings** → **Environment Variables**
3. Update or add:
   ```
   VITE_API_BASE_URL=https://your-backend.railway.app
   ```
4. **Redeploy** your frontend

### Step 6.4: Update CORS Origins (if needed)

If your Railway URL is different from the default, update in Railway:
```bash
DEXTER_FRONTEND_URL=https://ibm-dexter.vercel.app
DEXTER_CORS_ORIGINS=https://ibm-dexter.vercel.app
```

Railway will automatically redeploy.

### Step 6.5: Configure GitHub Webhooks

1. Go to your GitHub repository → **Settings** → **Webhooks**
2. Click **Add webhook**
3. Configure:
   - **Payload URL:** `https://your-backend.railway.app/api/v1/webhooks/github`
   - **Content type:** `application/json`
   - **Secret:** Use the webhook secret you entered in Settings UI
   - **Events:** Select "Pull requests" and "Pull request reviews"
4. Click **Add webhook**

---

## 7. Testing Checklist

After deployment, verify everything works:

- [ ] **Health Check:** Visit `https://your-backend.railway.app/health`
  - Should return: `{"status": "ok", "service": "IBM Dexter Backend", "version": "0.1.0"}`

- [ ] **Settings UI:** Visit `https://your-backend.railway.app/settings`
  - Configure GitHub token
  - Configure LLM provider credentials
  - Test all connections

- [ ] **Database Connection:** Check Railway logs for successful database connection

- [ ] **Frontend Connection:** 
  - Open https://ibm-dexter.vercel.app
  - Check browser console for API connection errors
  - Navigate to Settings page and verify it loads

- [ ] **GitHub Webhooks:**
  - Create a test PR in your repository
  - Check Railway logs for webhook receipt
  - Verify PR review is triggered

- [ ] **LLM Provider:**
  - Check logs for successful LLM initialization
  - Test a code review to verify LLM responses
  - Try different LLM providers via Settings UI

---

## 8. Quick Copy-Paste Configuration

### 🚀 Minimal Railway Environment Variables

Copy this entire block into Railway's environment variables (bulk edit mode):

```bash
# ============================================
# MINIMAL RAILWAY ENVIRONMENT VARIABLES
# Copy-paste this into Railway's bulk editor
# ============================================

# Application
DEXTER_APP_NAME=IBM Dexter AI Code Reviewer
DEXTER_ENVIRONMENT=production

# Database (Railway auto-injects this)
DATABASE_URL=${DATABASE_URL}

# Security (generate these once with: openssl rand -hex 32)
DEXTER_SECRET_KEY=<RUN: openssl rand -hex 32>
DEXTER_JWT_SECRET=<RUN: openssl rand -hex 32>

# CORS (your frontend URL)
DEXTER_FRONTEND_URL=https://ibm-dexter.vercel.app
DEXTER_CORS_ORIGINS=https://ibm-dexter.vercel.app

# API Configuration
DEXTER_API_HOST=0.0.0.0
DEXTER_API_PORT=8000

# ============================================
# ALL OTHER CREDENTIALS: Configure via UI
# Navigate to /settings after deployment
# ============================================
```

### 🔐 Commands to Generate Secrets

Run these commands locally and paste the output into Railway:

```bash
# Generate Secret Key
echo "DEXTER_SECRET_KEY=$(openssl rand -hex 32)"

# Generate JWT Secret
echo "DEXTER_JWT_SECRET=$(openssl rand -hex 32)"
```

---

## 9. Why UI-Based Configuration?

### Security Benefits
- ✅ **Encrypted Storage**: Credentials stored encrypted in database
- ✅ **No Dashboard Exposure**: Secrets not visible in Railway dashboard
- ✅ **Easy Rotation**: Update credentials without redeploying
- ✅ **Per-User Management**: Different users can have different credentials
- ✅ **Audit Trail**: Track who changed what and when

### Flexibility Benefits
- ✅ **Switch Providers**: Change LLM providers without redeploying
- ✅ **Instant Updates**: Update GitHub tokens immediately
- ✅ **Test Configurations**: Try different settings easily
- ✅ **Multi-Tenant**: Support multiple teams with different configs

### Operational Benefits
- ✅ **No Redeployment**: Credential changes don't require redeploy
- ✅ **Easier Onboarding**: New team members configure via UI
- ✅ **Better UX**: Non-technical users can manage credentials
- ✅ **Simplified Deployment**: Minimal environment variables to manage

### Development Benefits
- ✅ **Local Testing**: Test with different credentials easily
- ✅ **Environment Parity**: Same configuration method across environments
- ✅ **Version Control**: No secrets in git repositories
- ✅ **CI/CD Friendly**: Deployment pipelines don't need secret management

---
### Issue: "Script start.sh not found" or "Railpack could not determine how to build the app"

**Problem:** Railway is analyzing the root directory instead of the `/backend` directory, so it can't find your application files.

**Solution 1: Configure Root Directory in Railway Dashboard (RECOMMENDED)**
1. Go to your Railway project
2. Click on your service
3. Go to **Settings** tab
4. Find **Root Directory** setting
5. Set it to: `backend`
6. Click **Save**
7. Redeploy your service

**Solution 2: Use railway.toml Configuration File**
The project includes a `railway.toml` file in the root directory that tells Railway to use the backend directory. Make sure it's committed to your repository:

```toml
[build]
builder = "NIXPACKS"
buildCommand = "cd backend && pip install -r requirements.txt"

[deploy]
startCommand = "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

**Solution 3: Manual Build Configuration**
If the above don't work, manually configure in Railway Dashboard:
- **Root Directory**: `backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

**Verify Your Setup:**
After configuration, Railway should detect:
- ✅ Python 3.10+
- ✅ requirements.txt
- ✅ FastAPI application (main.py)
- ✅ PostgreSQL database connection

**Additional Configuration Files:**
The project includes these Railway-specific files:
- `/railway.toml` - Root configuration (tells Railway to use /backend)
- `/backend/railway.toml` - Backend-specific settings
- `/backend/nixpacks.toml` - Nixpacks build configuration
- `/backend/Procfile` - Process configuration


## 10. Troubleshooting

### Issue: "Module not found" errors

**Solution:** Ensure Root Directory is set to `/backend` in Railway settings.

### Issue: Database connection fails

**Solution:** 
1. Verify PostgreSQL service is running in Railway
2. Check that `DATABASE_URL` is present in environment variables
3. Ensure Railway has linked the database to your service
4. Check Railway logs for database connection errors

### Issue: CORS errors in frontend

**Solution:**
1. Verify `DEXTER_CORS_ORIGINS` includes your frontend URL
2. Ensure no trailing slashes in URLs
3. Check Railway logs for CORS-related errors
4. Verify `DEXTER_FRONTEND_URL` is set correctly

### Issue: Settings UI not loading

**Solution:**
1. Check Railway logs for backend errors
2. Verify database is connected and initialized
3. Ensure `/settings` endpoint is accessible
4. Check browser console for API errors

### Issue: GitHub webhooks not working

**Solution:**
1. Verify webhook URL is correct: `https://your-backend.railway.app/api/v1/webhooks/github`
2. Check that webhook secret in Settings UI matches GitHub webhook configuration
3. Review Railway logs for webhook receipt
4. Test webhook using GitHub's "Recent Deliveries" feature

### Issue: LLM provider errors

**Solution:**
1. Verify API keys are correct in Settings UI
2. Use "Test Connection" button to verify each provider
3. Check Railway logs for LLM initialization errors
4. Try OpenAI first (most reliable for cloud deployment)
5. Ensure you're not using Ollama on Railway (requires local installation)

### Issue: "Missing credentials" errors

**Solution:**
1. **First**, configure credentials via Settings UI at `/settings`
2. Don't try to add credentials as environment variables
3. Verify all required fields are filled in Settings UI
4. Click "Save Settings" and wait for confirmation

### Issue: Port binding errors

**Solution:**
- Ensure start command uses `--port $PORT` (Railway provides this)
- Don't hardcode port 8000 in production
- Check that `DEXTER_API_PORT=8000` is set (for internal reference)

### Viewing Logs

Access logs in Railway:
1. Go to your service in Railway Dashboard
2. Click **Deployments**
3. Select the latest deployment
4. View **Logs** tab

Look for:
- Database connection success messages
- Settings initialization logs
- LLM provider initialization
- Webhook receipt confirmations

---

## 📚 Additional Resources

- **Railway Documentation:** https://docs.railway.app/
- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **PostgreSQL on Railway:** https://docs.railway.app/databases/postgresql
- **IBM Dexter Frontend:** https://ibm-dexter.vercel.app/
- **GitHub Webhooks:** https://docs.github.com/en/webhooks
- **OpenAI API:** https://platform.openai.com/docs
- **IBM Watsonx:** https://www.ibm.com/products/watsonx-ai

---

## 🎉 Success!

Once deployed, your IBM Dexter backend will be available at:
```
https://your-backend.railway.app
```

And your complete system will be:
- **Frontend:** https://ibm-dexter.vercel.app
- **Backend:** https://your-backend.railway.app
- **Settings UI:** https://your-backend.railway.app/settings
- **Health Check:** https://your-backend.railway.app/health

### Remember:
1. ✅ **Minimal environment variables** in Railway (only 8 variables!)
2. ✅ **All credentials** configured via Settings UI
3. ✅ **No redeployment** needed for credential changes
4. ✅ **Secure and flexible** credential management

---

**Made with ❤️ by Bob**