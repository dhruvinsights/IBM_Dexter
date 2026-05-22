# 🚀 IBM Dexter Backend - Replit Deployment Guide

Complete step-by-step guide for deploying IBM Dexter backend on Replit for quick testing and development.

---

## 📋 Table of Contents

1. [Pre-Deployment Checklist](#1-pre-deployment-checklist)
2. [Replit Setup Steps](#2-replit-setup-steps)
3. [Environment Variables Configuration](#3-environment-variables-configuration)
4. [Database Setup](#4-database-setup)
5. [Testing the Deployment](#5-testing-the-deployment)
6. [Limitations & Workarounds](#6-limitations--workarounds)
7. [Next Steps](#7-next-steps)
8. [Troubleshooting Guide](#8-troubleshooting-guide)

---

## 1. Pre-Deployment Checklist

### ✅ What You Need Before Starting

- [ ] **Replit Account** - Free tier is sufficient for testing
- [ ] **GitHub Personal Access Token** - For repository integration
  - Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
  - Generate new token with `repo` scope
  - Save it securely - you'll need it for `DEXTER_GITHUB_TOKEN`
- [ ] **LLM Provider Choice** - Decide which AI provider to use:
  - **Ollama** (default) - Requires external hosting (not on Replit)
  - **OpenAI** - Requires API key (paid)
  - **IBM Watsonx** - Requires IBM Cloud account
  - **Anthropic Claude** - Requires API key (paid)

### 📦 What's Already Configured

The repository includes a `.replit` file that:
- ✅ Sets Python 3.11 as the runtime
- ✅ Configures port 8080 for the FastAPI server
- ✅ Automatically installs dependencies on startup
- ✅ Runs the backend with proper host/port settings

### ⚠️ Important Notes

- **Replit cannot run Ollama locally** - You'll need to use a cloud LLM provider or host Ollama externally
- **Free tier limitations** - Replit free tier has CPU/memory limits and will sleep after inactivity
- **SQLite is recommended** - PostgreSQL requires paid Replit plan
- **This is for testing only** - Not suitable for production use

---

## 2. Replit Setup Steps

### Step 1: Create Replit Account

1. Go to [replit.com](https://replit.com)
2. Click **Sign up** (or use GitHub/Google to sign in)
3. Verify your email address
4. Complete the onboarding (select "Python" as your preferred language)

### Step 2: Import GitHub Repository

**Option A: Import from GitHub URL**

1. Click **+ Create Repl** button
2. Select **Import from GitHub**
3. Paste your repository URL:
   ```
   https://github.com/YOUR_USERNAME/IBM-Dexter_AI_Code_Reviewer
   ```
4. Click **Import from GitHub**
5. Wait for Replit to clone the repository

**Option B: Fork and Import**

1. Fork the IBM Dexter repository on GitHub first
2. Follow Option A steps with your forked repository URL

### Step 3: Verify .replit Configuration

The `.replit` file should already be present. Verify it contains:

```toml
run = "cd backend && pip install -r requirements.txt -q && python -m uvicorn main:app --host 0.0.0.0 --port 8080"

[nix]
channel = "stable-24_05"

[languages.python]
version = "3.11"

[[ports]]
localPort = 8080
externalPort = 80
```

**If you need to modify it:**
- Click on `.replit` file in the file explorer
- Make changes
- Save (Ctrl+S or Cmd+S)

### Step 4: Configure Replit Secrets (Environment Variables)

Replit uses "Secrets" instead of `.env` files for security.

1. Click the **🔒 Secrets** icon in the left sidebar (or Tools → Secrets)
2. Add each environment variable as a separate secret (see Section 3 for complete list)
3. Click **Add new secret** for each variable

**Quick Setup - Minimal Required Secrets:**

```bash
# Required
DEXTER_GITHUB_TOKEN=ghp_your_github_token_here
DEXTER_LLM_PROVIDER=openai
DEXTER_OPENAI_API_KEY=sk-your_openai_key_here

# Database (SQLite - default)
DEXTER_DATABASE_URL=sqlite+aiosqlite:///./dexter.db

# Security
DEXTER_JWT_SECRET_KEY=your-random-secret-key-min-32-chars

# CORS (Important!)
DEXTER_CORS_ORIGINS=https://YOUR_REPL_ID.id.repl.co
```

**How to find your Repl URL:**
- After creating the Repl, look at the top of the page
- Your URL will be: `https://YOUR_REPL_NAME.YOUR_USERNAME.repl.co`
- Or click the **Open in new tab** button to see the full URL

### Step 5: Install Dependencies

**Automatic Installation (Recommended):**

1. Click the **Run** button at the top
2. Replit will automatically execute the `.replit` run command
3. Wait for dependencies to install (2-5 minutes)
4. Watch the console for any errors

**Manual Installation (If needed):**

Open the Shell tab and run:

```bash
cd backend
pip install -r requirements.txt
```

### Step 6: Start the Backend

**Using the Run Button:**

1. Click the **Run** button
2. The server will start on port 8080
3. Replit will show a webview with your API

**Using the Shell:**

```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8080
```

**Expected Output:**

```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Starting IBM Dexter backend in development mode
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080
```

---

## 3. Environment Variables Configuration

### 🔑 Required Environment Variables

Add these as Replit Secrets:

#### Core Application Settings

```bash
# Application
DEXTER_APP_NAME=IBM Dexter Backend
DEXTER_APP_VERSION=0.1.0
DEXTER_APP_ENV=development
DEXTER_APP_HOST=0.0.0.0
DEXTER_APP_PORT=8080
DEXTER_DEBUG=false
```

#### Database Configuration

```bash
# SQLite (Recommended for Replit)
DEXTER_DATABASE_URL=sqlite+aiosqlite:///./dexter.db
DEXTER_TEST_DATABASE_URL=sqlite+aiosqlite:///./dexter_test.db
DEXTER_DATABASE_ECHO=false
```

#### Security Settings

```bash
# JWT Configuration
DEXTER_JWT_SECRET_KEY=your-super-secret-key-at-least-32-characters-long
DEXTER_JWT_ALGORITHM=HS256
DEXTER_ACCESS_TOKEN_EXPIRE_MINUTES=60
DEXTER_REFRESH_TOKEN_EXPIRE_MINUTES=10080

# API Key (Optional - for webhook security)
DEXTER_API_KEY_HEADER_NAME=X-API-Key
DEXTER_API_KEY=dexter-replit-api-key-change-me
```

#### GitHub Integration

```bash
# GitHub Token (REQUIRED)
DEXTER_GITHUB_TOKEN=ghp_your_github_personal_access_token
DEXTER_GITHUB_WEBHOOK_SECRET=your-webhook-secret-if-using-webhooks
```

#### LLM Provider Configuration

**Option 1: OpenAI (Recommended for Replit)**

```bash
DEXTER_LLM_PROVIDER=openai
DEXTER_OPENAI_API_KEY=sk-your_openai_api_key_here
DEXTER_OPENAI_MODEL=gpt-4o-mini
```

**Option 2: IBM Watsonx**

```bash
DEXTER_LLM_PROVIDER=watsonx
DEXTER_WATSONX_API_KEY=your_watsonx_api_key
DEXTER_WATSONX_PROJECT_ID=your_project_id
DEXTER_WATSONX_URL=https://us-south.ml.cloud.ibm.com
DEXTER_WATSONX_MODEL=ibm/granite-13b-chat-v2
```

**Option 3: Anthropic Claude**

```bash
DEXTER_LLM_PROVIDER=anthropic
DEXTER_ANTHROPIC_API_KEY=sk-ant-your_anthropic_key
DEXTER_ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

**Option 4: Ollama (External Hosting Required)**

```bash
DEXTER_LLM_PROVIDER=ollama
DEXTER_OLLAMA_BASE_URL=https://your-ollama-server.com
DEXTER_OLLAMA_MODEL=qwen2.5-coder:14b
```

⚠️ **Note:** Ollama cannot run on Replit itself. You need to host it externally (e.g., on a VPS, Railway, or your local machine with ngrok).

#### CORS Configuration

```bash
# IMPORTANT: Set this to your Repl URL
DEXTER_CORS_ORIGINS=https://YOUR_REPL_NAME.YOUR_USERNAME.repl.co,http://localhost:3000
```

#### Optional: Embeddings Configuration

```bash
# For RAG/Knowledge Base features
DEXTER_EMBEDDING_PROVIDER=openai
DEXTER_OPENAI_EMBEDDING_MODEL=text-embedding-3-small
DEXTER_EMBEDDING_DIMENSION=1536
```

### 📝 How to Generate Secure Keys

**JWT Secret Key:**

```bash
# In Replit Shell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**API Key:**

```bash
# In Replit Shell
python -c "import secrets; print('dexter-' + secrets.token_urlsafe(16))"
```

---

## 4. Database Setup

### SQLite Configuration (Recommended)

**Why SQLite for Replit?**
- ✅ No additional setup required
- ✅ Works on free tier
- ✅ Sufficient for testing/development
- ✅ Data persists in Repl storage
- ⚠️ Limited to single instance
- ⚠️ Not suitable for production

**Configuration:**

```bash
DEXTER_DATABASE_URL=sqlite+aiosqlite:///./dexter.db
```

**Database Location:**
- File: `backend/dexter.db`
- Created automatically on first run
- Stored in Repl persistent storage

**Initialize Database:**

The database is automatically initialized on first startup. To manually initialize:

```bash
cd backend
python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"
```

### PostgreSQL Configuration (Paid Tier Only)

**Requirements:**
- Replit Hacker plan or higher
- PostgreSQL database add-on

**Configuration:**

1. Add PostgreSQL database in Replit:
   - Click **Database** icon in sidebar
   - Select **PostgreSQL**
   - Wait for provisioning

2. Update environment variable:

```bash
DEXTER_DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
```

3. Install additional dependency:

```bash
pip install asyncpg
```

### Database Backup

**Backup SQLite Database:**

```bash
# In Replit Shell
cd backend
cp dexter.db dexter.db.backup
```

**Download Database:**

1. Right-click on `dexter.db` in file explorer
2. Select **Download**
3. Save to your local machine

---

## 5. Testing the Deployment

### Step 1: Access the API

**Find Your API URL:**

1. Click the **Open in new tab** button in Replit
2. Your API is at: `https://YOUR_REPL_NAME.YOUR_USERNAME.repl.co`

**API Documentation:**

- Swagger UI: `https://YOUR_REPL_NAME.YOUR_USERNAME.repl.co/docs`
- ReDoc: `https://YOUR_REPL_NAME.YOUR_USERNAME.repl.co/redoc`

### Step 2: Test Health Endpoint

**Using Browser:**

Navigate to: `https://YOUR_REPL_NAME.YOUR_USERNAME.repl.co/api/v1/health`

**Using curl:**

```bash
curl https://YOUR_REPL_NAME.YOUR_USERNAME.repl.co/api/v1/health
```

**Expected Response:**

```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "development"
}
```

### Step 3: Test API Endpoints

**1. Test Settings Endpoint:**

```bash
curl https://YOUR_REPL_NAME.YOUR_USERNAME.repl.co/api/v1/settings
```

**2. Test GitHub Integration:**

```bash
curl -H "X-API-Key: your-api-key" \
  https://YOUR_REPL_NAME.YOUR_USERNAME.repl.co/api/v1/repositories
```

**3. Test LLM Provider:**

```bash
curl -X POST https://YOUR_REPL_NAME.YOUR_USERNAME.repl.co/api/v1/reviews/test \
  -H "Content-Type: application/json" \
  -d '{"code": "def hello(): print(\"Hello\")"}'
```

### Step 4: Check Logs

**View Logs in Replit:**

1. Look at the **Console** tab
2. Check for any errors or warnings
3. Verify startup messages

**Common Log Messages:**

```
✅ INFO: Starting IBM Dexter backend in development mode
✅ INFO: Uvicorn running on http://0.0.0.0:8080
✅ INFO: Application startup complete
```

### Step 5: Test with Frontend

**If deploying frontend separately:**

1. Deploy frontend to Vercel/Netlify
2. Set `VITE_API_URL` to your Repl URL
3. Update `DEXTER_CORS_ORIGINS` to include frontend URL
4. Test end-to-end functionality

---

## 6. Limitations & Workarounds

### Free Tier Limitations

#### 1. **Repl Sleep Behavior**

**Problem:**
- Repl goes to sleep after 1 hour of inactivity
- Cold start takes 10-30 seconds

**Workarounds:**

**Option A: UptimeRobot (Free)**

1. Sign up at [uptimerobot.com](https://uptimerobot.com)
2. Add new monitor:
   - Type: HTTP(s)
   - URL: `https://YOUR_REPL_NAME.YOUR_USERNAME.repl.co/api/v1/health`
   - Interval: 5 minutes
3. This pings your Repl every 5 minutes to keep it awake

**Option B: Cron-job.org (Free)**

1. Sign up at [cron-job.org](https://cron-job.org)
2. Create new cron job:
   - URL: Your Repl health endpoint
   - Schedule: Every 5 minutes
3. Enable the job

**Option C: Simple Ping Script**

```bash
# Run on your local machine or another server
while true; do
  curl https://YOUR_REPL_NAME.YOUR_USERNAME.repl.co/api/v1/health
  sleep 300  # 5 minutes
done
```

#### 2. **CPU/Memory Limits**

**Problem:**
- Limited CPU and RAM on free tier
- May timeout on heavy operations

**Workarounds:**

- Use lightweight LLM models (gpt-4o-mini instead of gpt-4)
- Reduce concurrent requests
- Optimize database queries
- Disable unnecessary features

#### 3. **Storage Limits**

**Problem:**
- Limited persistent storage
- Database can grow large

**Workarounds:**

- Regular database cleanup
- Limit review history retention
- Use external storage for large files
- Monitor database size:

```bash
cd backend
du -h dexter.db
```

#### 4. **No Ollama Support**

**Problem:**
- Cannot run Ollama on Replit

**Solutions:**

**Option A: Use Cloud LLM (Recommended)**
- OpenAI, Anthropic, or Watsonx
- Pay-per-use pricing
- No infrastructure needed

**Option B: External Ollama Hosting**

1. **Railway.app:**
   - Deploy Ollama container
   - Get public URL
   - Set `DEXTER_OLLAMA_BASE_URL`

2. **Your Local Machine + ngrok:**
   ```bash
   # On your machine
   ollama serve
   
   # In another terminal
   ngrok http 11434
   
   # Use ngrok URL in Replit
   DEXTER_OLLAMA_BASE_URL=https://abc123.ngrok.io
   ```

3. **VPS/Cloud Server:**
   - Deploy Ollama on DigitalOcean/AWS/GCP
   - Configure firewall
   - Use public IP/domain

### Performance Optimization

**1. Reduce Dependency Installation Time:**

Edit `.replit` to cache dependencies:

```toml
run = "cd backend && pip install -r requirements.txt -q --cache-dir=/tmp/pip-cache && python -m uvicorn main:app --host 0.0.0.0 --port 8080"
```

**2. Use Minimal Requirements:**

If you don't need all features, create `requirements-replit.txt`:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
aiosqlite==0.19.0
openai>=1.0.0
PyGithub==2.1.1
python-jose[cryptography]==3.3.0
python-dotenv==1.0.0
```

Update `.replit`:

```toml
run = "cd backend && pip install -r requirements-replit.txt -q && python -m uvicorn main:app --host 0.0.0.0 --port 8080"
```

**3. Optimize Startup:**

Add to `main.py`:

```python
# Disable unnecessary features for Replit
if os.getenv("REPLIT") == "true":
    # Disable background tasks
    # Reduce logging
    # Skip heavy initializations
    pass
```

---

## 7. Next Steps

### When to Upgrade from Replit

Consider moving to a production platform when:

- ✅ You need 24/7 uptime without sleep
- ✅ You need better performance (CPU/RAM)
- ✅ You need PostgreSQL or other databases
- ✅ You need custom domains
- ✅ You need to run Ollama locally
- ✅ You're ready for production deployment

### Recommended Production Platforms

#### 1. **Railway.app** (Easiest)

**Pros:**
- Simple deployment from GitHub
- PostgreSQL included
- Generous free tier
- Can run Ollama containers

**Setup:**
1. Connect GitHub repository
2. Add PostgreSQL database
3. Set environment variables
4. Deploy

**Cost:** ~$5-20/month

#### 2. **Render.com**

**Pros:**
- Free tier available
- PostgreSQL included
- Auto-deploy from GitHub
- Good documentation

**Setup:**
1. Create Web Service from GitHub
2. Add PostgreSQL database
3. Configure environment
4. Deploy

**Cost:** Free tier available, paid from $7/month

#### 3. **Fly.io**

**Pros:**
- Global edge deployment
- Can run Ollama
- Good free tier
- Docker-based

**Setup:**
1. Install flyctl CLI
2. Run `fly launch`
3. Configure `fly.toml`
4. Deploy with `fly deploy`

**Cost:** Free tier available, paid from $5/month

#### 4. **AWS/GCP/Azure** (Enterprise)

**Pros:**
- Full control
- Enterprise features
- Scalable
- Can run anything

**Cons:**
- Complex setup
- Higher cost
- Requires DevOps knowledge

**Cost:** Varies, typically $50+/month

### Migration Checklist

When moving from Replit to production:

- [ ] Export database backup
- [ ] Document all environment variables
- [ ] Test with production LLM provider
- [ ] Set up PostgreSQL database
- [ ] Configure custom domain
- [ ] Set up SSL/TLS certificates
- [ ] Configure monitoring and logging
- [ ] Set up automated backups
- [ ] Configure CI/CD pipeline
- [ ] Update CORS origins
- [ ] Test all endpoints
- [ ] Update frontend API URL

### Monitoring and Maintenance

**On Replit:**

1. **Check Logs Regularly:**
   - Monitor Console tab
   - Look for errors/warnings

2. **Monitor Database Size:**
   ```bash
   cd backend
   du -h dexter.db
   ```

3. **Test Endpoints Weekly:**
   - Health check
   - Key API endpoints
   - LLM integration

4. **Backup Database:**
   - Weekly backups
   - Download to local machine
   - Store in cloud storage

**Set Up Alerts:**

Use UptimeRobot or similar to get notified when:
- Repl goes down
- Response time is slow
- Errors occur

---

## 8. Troubleshooting Guide

### Common Issues and Solutions

#### Issue 1: "Module not found" Error

**Symptoms:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solutions:**

1. **Reinstall dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt --force-reinstall
   ```

2. **Check Python version:**
   ```bash
   python --version  # Should be 3.11+
   ```

3. **Clear pip cache:**
   ```bash
   pip cache purge
   pip install -r requirements.txt
   ```

#### Issue 2: Port Binding Error

**Symptoms:**
```
ERROR: [Errno 98] Address already in use
```

**Solutions:**

1. **Stop existing process:**
   - Click **Stop** button in Replit
   - Wait 5 seconds
   - Click **Run** again

2. **Kill process manually:**
   ```bash
   pkill -f uvicorn
   ```

3. **Use different port (if needed):**
   ```bash
   python -m uvicorn main:app --host 0.0.0.0 --port 8081
   ```

#### Issue 3: Database Connection Error

**Symptoms:**
```
sqlalchemy.exc.OperationalError: unable to open database file
```

**Solutions:**

1. **Check database path:**
   ```bash
   cd backend
   ls -la dexter.db
   ```

2. **Create database directory:**
   ```bash
   cd backend
   mkdir -p data
   ```

3. **Fix permissions:**
   ```bash
   chmod 644 dexter.db
   ```

4. **Reset database:**
   ```bash
   cd backend
   rm dexter.db
   # Restart the app to recreate
   ```

#### Issue 4: CORS Error

**Symptoms:**
```
Access to fetch at 'https://...' from origin 'https://...' has been blocked by CORS policy
```

**Solutions:**

1. **Update CORS origins in Secrets:**
   ```bash
   DEXTER_CORS_ORIGINS=https://your-frontend.vercel.app,https://your-repl.repl.co
   ```

2. **Check for typos:**
   - No trailing slashes
   - Correct protocol (https://)
   - Exact domain match

3. **Restart the server** after changing CORS settings

#### Issue 5: GitHub Token Error

**Symptoms:**
```
401 Unauthorized: Bad credentials
```

**Solutions:**

1. **Verify token in Secrets:**
   - Check `DEXTER_GITHUB_TOKEN` is set
   - Token should start with `ghp_`

2. **Check token permissions:**
   - Go to GitHub Settings → Developer settings
   - Verify token has `repo` scope
   - Regenerate if needed

3. **Test token:**
   ```bash
   curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
   ```

#### Issue 6: LLM Provider Error

**Symptoms:**
```
Error: Could not connect to LLM provider
```

**Solutions:**

**For OpenAI:**
1. Verify API key in Secrets
2. Check API key is valid:
   ```bash
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer YOUR_KEY"
   ```
3. Verify you have credits

**For Ollama:**
1. Check `DEXTER_OLLAMA_BASE_URL` is accessible
2. Test connection:
   ```bash
   curl https://your-ollama-url/api/tags
   ```
3. Verify model is pulled

**For Watsonx:**
1. Check API key and project ID
2. Verify region URL is correct
3. Test authentication

#### Issue 7: Slow Performance

**Symptoms:**
- Requests timeout
- Slow response times
- High CPU usage

**Solutions:**

1. **Use lighter LLM model:**
   ```bash
   DEXTER_OPENAI_MODEL=gpt-4o-mini  # Instead of gpt-4
   ```

2. **Reduce token limits:**
   ```bash
   DEXTER_LLM_MAX_TOKENS=1000  # Instead of 2000
   ```

3. **Optimize database:**
   ```bash
   cd backend
   sqlite3 dexter.db "VACUUM;"
   ```

4. **Clear old data:**
   ```bash
   # Delete old reviews (older than 30 days)
   sqlite3 dexter.db "DELETE FROM reviews WHERE created_at < datetime('now', '-30 days');"
   ```

#### Issue 8: Repl Won't Start

**Symptoms:**
- Repl shows error on startup
- Console shows crash

**Solutions:**

1. **Check .replit file:**
   - Verify syntax is correct
   - Check file paths

2. **View full error:**
   - Look at Console tab
   - Check for Python errors

3. **Test manually:**
   ```bash
   cd backend
   python main.py
   ```

4. **Reset Repl:**
   - Fork the Repl
   - Or delete and recreate

#### Issue 9: Environment Variables Not Loading

**Symptoms:**
```
KeyError: 'DEXTER_GITHUB_TOKEN'
```

**Solutions:**

1. **Verify Secrets are set:**
   - Click Secrets icon
   - Check all required variables

2. **Restart Repl:**
   - Stop and start again
   - Secrets load on startup

3. **Check variable names:**
   - Must match exactly (case-sensitive)
   - No extra spaces

4. **Test in Shell:**
   ```bash
   echo $DEXTER_GITHUB_TOKEN
   ```

#### Issue 10: Database Locked Error

**Symptoms:**
```
sqlite3.OperationalError: database is locked
```

**Solutions:**

1. **Close other connections:**
   ```bash
   pkill -f python
   ```

2. **Wait and retry:**
   - SQLite locks are usually temporary
   - Wait 10 seconds and try again

3. **Check for zombie processes:**
   ```bash
   ps aux | grep python
   ```

4. **Restart Repl** if issue persists

### Getting Help

**If you're still stuck:**

1. **Check Replit Status:**
   - Visit [status.replit.com](https://status.replit.com)
   - Check for ongoing issues

2. **Replit Community:**
   - [Replit Ask Forum](https://ask.replit.com)
   - Search for similar issues

3. **IBM Dexter Issues:**
   - Check GitHub Issues
   - Create new issue with:
     - Error message
     - Steps to reproduce
     - Environment details

4. **Enable Debug Mode:**
   ```bash
   DEXTER_DEBUG=true
   DEXTER_LOG_LEVEL=DEBUG
   ```

5. **Collect Logs:**
   - Copy full console output
   - Include in support request

---

## 📚 Additional Resources

### Documentation

- [Replit Docs](https://docs.replit.com)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org)
- [GitHub API Docs](https://docs.github.com/en/rest)

### Tutorials

- [Replit Python Tutorial](https://docs.replit.com/tutorials/python)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [SQLite Tutorial](https://www.sqlitetutorial.net)

### Tools

- [UptimeRobot](https://uptimerobot.com) - Keep Repl awake
- [ngrok](https://ngrok.com) - Expose local Ollama
- [Postman](https://www.postman.com) - API testing
- [DB Browser for SQLite](https://sqlitebrowser.org) - Database viewer

---

## ✅ Quick Reference

### Essential Commands

```bash
# Install dependencies
cd backend && pip install -r requirements.txt

# Start server
python -m uvicorn main:app --host 0.0.0.0 --port 8080

# Check database
cd backend && ls -lh dexter.db

# View logs
# (Check Console tab in Replit)

# Test health endpoint
curl https://YOUR_REPL.repl.co/api/v1/health

# Backup database
cd backend && cp dexter.db dexter.db.backup
```

### Required Secrets (Minimum)

```bash
DEXTER_GITHUB_TOKEN=ghp_xxxxx
DEXTER_LLM_PROVIDER=openai
DEXTER_OPENAI_API_KEY=sk-xxxxx
DEXTER_DATABASE_URL=sqlite+aiosqlite:///./dexter.db
DEXTER_JWT_SECRET_KEY=your-secret-key-32-chars-min
DEXTER_CORS_ORIGINS=https://YOUR_REPL.repl.co
```

### Important URLs

- **Your API:** `https://YOUR_REPL_NAME.YOUR_USERNAME.repl.co`
- **API Docs:** `https://YOUR_REPL_NAME.YOUR_USERNAME.repl.co/docs`
- **Health Check:** `https://YOUR_REPL_NAME.YOUR_USERNAME.repl.co/api/v1/health`

---

## 🎉 Success Checklist

After deployment, verify:

- [ ] Repl starts without errors
- [ ] Health endpoint returns 200 OK
- [ ] API docs are accessible at `/docs`
- [ ] GitHub token is working
- [ ] LLM provider is responding
- [ ] Database is created and accessible
- [ ] CORS is configured correctly
- [ ] All required secrets are set
- [ ] UptimeRobot is monitoring (optional)
- [ ] Frontend can connect (if applicable)

---

## 📝 Notes

- **This guide is for development/testing only**
- **Not recommended for production use**
- **Free tier has limitations**
- **Consider upgrading to Railway/Render for production**
- **Keep your secrets secure - never commit them**
- **Regular backups are essential**

---

**Need help?** Open an issue on GitHub or ask in the Replit community!

**Ready for production?** Check out the [Railway Deployment Guide](RAILWAY_DEPLOYMENT_GUIDE.md) or [Render Deployment Guide](RENDER_DEPLOYMENT_GUIDE.md).

---

*Last updated: 2026-05-22*
*Version: 1.0.0*
*Tested on: Replit Free Tier, Python 3.11*