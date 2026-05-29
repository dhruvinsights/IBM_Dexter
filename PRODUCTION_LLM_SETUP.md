# Production LLM Provider Setup

## 🎯 Current Status

✅ **Frontend Connected** - Your frontend at https://ibm-dexter.vercel.app is successfully connecting to the backend
✅ **Backend Running** - Your backend at https://ibmdexter-production.up.railway.app is operational
✅ **GitHub Connected** - Your GitHub token is working
❌ **LLM Provider Missing** - You need to configure a cloud LLM provider

## ⚠️ Why Ollama Doesn't Work in Production

The errors you're seeing:
```
RuntimeError: No available LLM providers found
INFO: "GET /api/v1/settings/ollama/health HTTP/1.1" 502 Bad Gateway
```

**Reason:** Ollama requires local installation and can't run in Railway's cloud environment. It's designed for local development only.

## 🚀 Solution: Configure a Cloud LLM Provider

You have three options for production:

### Option 1: OpenAI (Recommended - Easiest)

**Pros:**
- Most reliable and well-tested
- Best performance
- Simple setup
- Pay-as-you-go pricing

**Setup:**
1. Get API key: https://platform.openai.com/api-keys
2. Add to Railway environment variables:
   ```
   DEXTER_OPENAI_API_KEY=sk-...your-key...
   DEXTER_LLM_PROVIDER=openai
   DEXTER_DEFAULT_LLM_PROVIDER=openai
   ```
3. Railway will auto-redeploy
4. Test in Settings UI

**Cost:** ~$0.002 per code review (very affordable)

### Option 2: IBM Watsonx (Enterprise)

**Pros:**
- IBM enterprise support
- Data stays in IBM cloud
- Granite models optimized for code

**Setup:**
1. Get IBM Cloud API key: https://cloud.ibm.com/iam/apikeys
2. Get Watsonx project ID from your Watsonx instance
3. Add to Railway:
   ```
   DEXTER_WATSONX_API_KEY=your-ibm-cloud-api-key
   DEXTER_WATSONX_PROJECT_ID=your-project-id
   DEXTER_LLM_PROVIDER=watsonx
   DEXTER_DEFAULT_LLM_PROVIDER=watsonx
   ```

### Option 3: Anthropic Claude

**Pros:**
- Excellent code understanding
- Long context window
- Good for complex reviews

**Setup:**
1. Get API key: https://console.anthropic.com/
2. Add to Railway:
   ```
   DEXTER_ANTHROPIC_API_KEY=sk-ant-...your-key...
   DEXTER_LLM_PROVIDER=anthropic
   DEXTER_DEFAULT_LLM_PROVIDER=anthropic
   ```

## 📋 Quick Setup (OpenAI - Recommended)

### Step 1: Get OpenAI API Key
1. Go to: https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-`)

### Step 2: Add to Railway
1. Go to Railway Dashboard → Your Backend Service → Variables
2. Add these variables:
   ```
   DEXTER_OPENAI_API_KEY=sk-...your-actual-key...
   DEXTER_LLM_PROVIDER=openai
   DEXTER_DEFAULT_LLM_PROVIDER=openai
   DEXTER_OPENAI_MODEL=gpt-4o-mini
   ```
3. Save (Railway will auto-redeploy)

### Step 3: Verify
1. Wait for Railway to redeploy (~2 minutes)
2. Visit: https://ibm-dexter.vercel.app/settings
3. Check "AI Agents" section - should show "Connected"
4. No more "No available LLM providers found" errors

## 🔍 Understanding the Logs

### Good Logs (What You Want to See):
```
INFO: "GET /api/v1/repositories HTTP/1.1" 200 OK
INFO: "GET /api/v1/reviews HTTP/1.1" 200 OK
INFO: "GET /api/v1/pull-requests HTTP/1.1" 200 OK
```
✅ These are working! Your frontend IS connected.

### Expected Errors (Can Ignore):
```
ERROR: Failed to connect to Db2: ...
```
✅ Normal - you're using PostgreSQL, not Db2. This is just a fallback check.

### Errors to Fix (LLM Provider):
```
RuntimeError: No available LLM providers found
INFO: "GET /api/v1/agents HTTP/1.1" 500 Internal Server Error
```
❌ These will disappear once you add OpenAI/Watsonx/Anthropic API key.

## 💰 Cost Estimates

### OpenAI (gpt-4o-mini):
- Per code review: ~$0.002 (very cheap)
- 1000 reviews: ~$2
- Best for: Most users

### OpenAI (gpt-4):
- Per code review: ~$0.02
- 1000 reviews: ~$20
- Best for: Complex enterprise code

### Watsonx:
- Pricing varies by IBM contract
- Best for: IBM enterprise customers

### Anthropic Claude:
- Per code review: ~$0.015
- 1000 reviews: ~$15
- Best for: Complex analysis

## 🎯 Recommended Configuration

For production, use this Railway configuration:

```bash
# Core Settings (already configured)
DEXTER_ENVIRONMENT=production
DEXTER_FRONTEND_URL=https://ibm-dexter.vercel.app
DEXTER_CORS_ORIGINS=https://ibm-dexter.vercel.app

# LLM Provider (ADD THIS)
DEXTER_OPENAI_API_KEY=sk-...your-key...
DEXTER_LLM_PROVIDER=openai
DEXTER_DEFAULT_LLM_PROVIDER=openai
DEXTER_OPENAI_MODEL=gpt-4o-mini

# Database (already configured by Railway)
DATABASE_URL=${DATABASE_URL}

# Security (already configured)
DEXTER_SECRET_KEY=...
DEXTER_JWT_SECRET=...
```

## 📝 Quick Reference: Railway Environment Variables

### Minimal Required (Already Set):
```bash
DEXTER_ENVIRONMENT=production
DEXTER_FRONTEND_URL=https://ibm-dexter.vercel.app
DEXTER_CORS_ORIGINS=https://ibm-dexter.vercel.app
DATABASE_URL=${DATABASE_URL}
DEXTER_SECRET_KEY=...
DEXTER_JWT_SECRET=...
```

### LLM Provider (MUST ADD):
```bash
# Option 1: OpenAI (Recommended)
DEXTER_OPENAI_API_KEY=sk-...
DEXTER_LLM_PROVIDER=openai
DEXTER_DEFAULT_LLM_PROVIDER=openai

# Option 2: Watsonx
DEXTER_WATSONX_API_KEY=...
DEXTER_WATSONX_PROJECT_ID=...
DEXTER_LLM_PROVIDER=watsonx
DEXTER_DEFAULT_LLM_PROVIDER=watsonx

# Option 3: Anthropic
DEXTER_ANTHROPIC_API_KEY=sk-ant-...
DEXTER_LLM_PROVIDER=anthropic
DEXTER_DEFAULT_LLM_PROVIDER=anthropic
```

## ✅ Success Checklist

After adding LLM provider:
- [ ] Railway redeployed successfully
- [ ] No "No available LLM providers found" errors in logs
- [ ] Settings page shows AI Agents as "Connected"
- [ ] Can trigger code reviews
- [ ] Reviews complete successfully

## 🆘 Still Having Issues?

If you still see errors after adding OpenAI key:
1. Verify the API key is correct (starts with `sk-`)
2. Check Railway logs for new errors
3. Ensure `DEXTER_LLM_PROVIDER=openai` is set
4. Try redeploying manually in Railway
5. Check OpenAI account has credits/billing enabled

## 🔧 Advanced Configuration

### Using Multiple Providers
You can configure multiple providers and switch between them:
```bash
# Configure all three
DEXTER_OPENAI_API_KEY=sk-...
DEXTER_WATSONX_API_KEY=...
DEXTER_WATSONX_PROJECT_ID=...
DEXTER_ANTHROPIC_API_KEY=sk-ant-...

# Set default
DEXTER_DEFAULT_LLM_PROVIDER=openai
```

### Model Selection
```bash
# OpenAI models
DEXTER_OPENAI_MODEL=gpt-4o-mini          # Fastest, cheapest
DEXTER_OPENAI_MODEL=gpt-4o               # Balanced
DEXTER_OPENAI_MODEL=gpt-4                # Most capable

# Watsonx models
DEXTER_WATSONX_MODEL=ibm/granite-13b-chat-v2
DEXTER_WATSONX_MODEL=ibm/granite-20b-code-instruct

# Anthropic models
DEXTER_ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
DEXTER_ANTHROPIC_MODEL=claude-3-opus-20240229
```

## 📊 Monitoring Usage

### OpenAI
- Dashboard: https://platform.openai.com/usage
- Set usage limits to control costs
- Monitor API key usage

### Watsonx
- IBM Cloud Dashboard
- Watsonx project usage metrics

### Anthropic
- Console: https://console.anthropic.com/
- Usage and billing section

## 🎓 Next Steps

After configuring your LLM provider:

1. **Test Code Reviews**
   - Create a test PR in your repository
   - Trigger a review from Dexter
   - Verify AI-generated insights

2. **Configure Agents**
   - Visit Settings → AI Agents
   - Enable/disable specific agents
   - Customize agent behavior

3. **Set Up Webhooks**
   - Configure GitHub webhooks for automatic reviews
   - See webhook documentation

4. **Monitor Performance**
   - Check review quality
   - Monitor response times
   - Adjust model selection if needed

## 📚 Additional Resources

- [Backend Configuration Guide](backend/README.md)
- [Railway Deployment Guide](RAILWAY_DEPLOYMENT_GUIDE.md)
- [Frontend Setup](frontend/README.md)
- [API Documentation](backend/app/api/v1/endpoints/)