# 🚨 Railway Production - Quick Fix Guide

## Your Current Situation

✅ **Frontend IS Connected** - https://ibm-dexter.vercel.app successfully connects to backend
✅ **Backend IS Running** - https://ibmdexter-production.up.railway.app is operational
✅ **GitHub IS Working** - Your GitHub token is configured correctly
❌ **LLM Provider Missing** - This is the ONLY issue

## The Problem

You're seeing these errors:
```
RuntimeError: No available LLM providers found
INFO: "GET /api/v1/settings/ollama/health HTTP/1.1" 502 Bad Gateway
```

**Why:** Ollama requires local installation and doesn't work in Railway's cloud environment.

## The Solution (5 Minutes)

### Step 1: Get OpenAI API Key
1. Visit: https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-`)

### Step 2: Add to Railway
1. Go to Railway Dashboard
2. Select your backend service
3. Click "Variables" tab
4. Add these 4 variables:

```bash
DEXTER_OPENAI_API_KEY=sk-...paste-your-key-here...
DEXTER_LLM_PROVIDER=openai
DEXTER_DEFAULT_LLM_PROVIDER=openai
DEXTER_OPENAI_MODEL=gpt-4o-mini
```

5. Click "Save" (Railway will auto-redeploy)

### Step 3: Verify (2 minutes later)
1. Wait for Railway to finish redeploying
2. Visit: https://ibm-dexter.vercel.app/settings
3. Check "AI Agents" section - should show "Connected" ✅
4. No more errors!

## Cost
- **gpt-4o-mini**: ~$0.002 per code review (very cheap)
- 1000 reviews = ~$2

## What These Logs Mean

### ✅ Good Logs (Already Working):
```
INFO: "GET /api/v1/repositories HTTP/1.1" 200 OK
INFO: "GET /api/v1/reviews HTTP/1.1" 200 OK
INFO: "GET /api/v1/pull-requests HTTP/1.1" 200 OK
```
Your frontend IS connected! These are successful.

### ⚠️ Expected Logs (Can Ignore):
```
ERROR: Failed to connect to Db2: ...
```
Normal - you're using PostgreSQL. This is just a fallback check.

### ❌ Logs That Will Disappear After Fix:
```
RuntimeError: No available LLM providers found
INFO: "GET /api/v1/agents HTTP/1.1" 500 Internal Server Error
```
These will go away once you add the OpenAI key.

## Alternative Providers

Don't want to use OpenAI? See `PRODUCTION_LLM_SETUP.md` for:
- **IBM Watsonx** (enterprise, Granite models)
- **Anthropic Claude** (excellent code understanding)

## Need More Help?

See the complete guide: `PRODUCTION_LLM_SETUP.md`
- Detailed setup for all providers
- Cost comparisons
- Troubleshooting
- Advanced configuration