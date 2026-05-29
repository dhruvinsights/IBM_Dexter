# 🚀 Vercel Frontend Configuration Guide

## 🎯 Connect Frontend to Railway Backend

Your backend is now live at: **`https://ibmdexter-production.up.railway.app`**

Your frontend is deployed at: **`https://ibm-dexter.vercel.app`**

This guide will help you connect them together.

---

## 📋 Quick Setup Overview

1. **Configure Vercel Environment Variable** → Point frontend to Railway backend
2. **Redeploy Frontend** → Apply the new configuration
3. **Update Railway CORS Settings** → Allow frontend to access backend
4. **Test Connection** → Verify everything works

---

## Step 1: Configure Vercel Environment Variables

### 1.1 Access Vercel Dashboard

1. Go to **Vercel Dashboard**: https://vercel.com/dashboard
2. Select your project: **ibm-dexter**
3. Go to **Settings** → **Environment Variables**

### 1.2 Add Backend URL Variable

Add the following environment variable:

| Field | Value |
|-------|-------|
| **Name** | `VITE_API_URL` |
| **Value** | `https://ibmdexter-production.up.railway.app/api/v1` |
| **Environment** | ✅ Production, ✅ Preview, ✅ Development |

> ⚠️ **Important Notes:**
> - The variable name is `VITE_API_URL` (not `VITE_API_BASE_URL`)
> - Include `/api/v1` at the end of the URL
> - No trailing slash after `/api/v1`
> - Select ALL three environments (Production, Preview, Development)

### 1.3 Save Configuration

1. Click **Save** button
2. Vercel will show a confirmation message
3. Note: Changes won't take effect until you redeploy

---

## Step 2: Redeploy Frontend

After adding the environment variable, you must redeploy:

### Option A: Redeploy from Vercel Dashboard

1. Go to **Deployments** tab in your Vercel project
2. Find the latest deployment
3. Click the **⋯** (three dots) menu
4. Select **Redeploy**
5. Confirm the redeployment
6. Wait for deployment to complete (usually 1-2 minutes)

### Option B: Trigger New Deployment via Git

1. Make a small change to your repository (e.g., update README)
2. Commit and push to your main branch
3. Vercel will automatically deploy

### Verify Deployment

Once deployment completes:
- ✅ Status shows "Ready"
- ✅ Visit `https://ibm-dexter.vercel.app`
- ✅ Open browser DevTools (F12) → Console
- ✅ Look for API calls to `https://ibmdexter-production.up.railway.app`

---

## Step 3: Update Railway Backend CORS Settings

Your backend needs to allow requests from the Vercel frontend.

### 3.1 Access Railway Dashboard

1. Go to **Railway Dashboard**: https://railway.app/dashboard
2. Select your **backend service** (not the database)
3. Go to **Variables** tab

### 3.2 Add/Update CORS Variables

Add or update these environment variables:

```bash
DEXTER_CORS_ORIGINS=https://ibm-dexter.vercel.app
DEXTER_FRONTEND_URL=https://ibm-dexter.vercel.app
```

> 💡 **Tip:** Use the "Raw Editor" in Railway to paste both variables at once:
> ```
> DEXTER_CORS_ORIGINS=https://ibm-dexter.vercel.app
> DEXTER_FRONTEND_URL=https://ibm-dexter.vercel.app
> ```

### 3.3 Save and Redeploy

1. Click **Save** or **Add Variables**
2. Railway will automatically redeploy your backend
3. Wait for deployment to complete (check the Deployments tab)
4. Verify backend is running at: `https://ibmdexter-production.up.railway.app/health`

---

## Step 4: Test the Connection

### 4.1 Test Backend Health

Open in your browser:
```
https://ibmdexter-production.up.railway.app/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "IBM Dexter Backend",
  "version": "0.1.0"
}
```

### 4.2 Test Frontend Connection

1. Visit: `https://ibm-dexter.vercel.app`
2. Open browser DevTools (F12)
3. Go to **Console** tab
4. Look for API calls to Railway backend
5. Check for any CORS errors (there should be none)

### 4.3 Test API Endpoints

1. Navigate to **Dashboard** page
2. Check if data loads correctly
3. Try navigating to **Settings** page
4. Verify no error messages appear

### 4.4 Check Network Tab

1. Open DevTools → **Network** tab
2. Refresh the page
3. Look for requests to `ibmdexter-production.up.railway.app`
4. Verify responses are successful (200 status codes)

---

## ✅ Verification Checklist

Use this checklist to ensure everything is configured correctly:

- [ ] **Vercel Environment Variable Set**
  - [ ] Variable name is `VITE_API_URL`
  - [ ] Value is `https://ibmdexter-production.up.railway.app/api/v1`
  - [ ] Applied to Production, Preview, and Development
  
- [ ] **Frontend Redeployed**
  - [ ] Deployment completed successfully
  - [ ] Status shows "Ready" in Vercel
  
- [ ] **Railway CORS Configured**
  - [ ] `DEXTER_CORS_ORIGINS` set to `https://ibm-dexter.vercel.app`
  - [ ] `DEXTER_FRONTEND_URL` set to `https://ibm-dexter.vercel.app`
  - [ ] Backend redeployed after adding variables
  
- [ ] **Connection Tests Passed**
  - [ ] Backend health check returns OK
  - [ ] Frontend loads without errors
  - [ ] No CORS errors in browser console
  - [ ] API calls reaching Railway backend
  - [ ] Data loading correctly in frontend

---

## 🔧 Troubleshooting

### Issue: CORS Error

**Error Message:**
```
Access to fetch at 'https://ibmdexter-production.up.railway.app/api/v1/...' 
from origin 'https://ibm-dexter.vercel.app' has been blocked by CORS policy
```

**Solutions:**

1. **Check Railway CORS Variables:**
   - Go to Railway → Variables tab
   - Verify `DEXTER_CORS_ORIGINS=https://ibm-dexter.vercel.app`
   - Ensure no trailing slashes
   - Ensure no typos in the URL

2. **Redeploy Backend:**
   - After updating CORS variables, Railway should auto-redeploy
   - If not, manually trigger a redeploy
   - Wait for deployment to complete

3. **Clear Browser Cache:**
   - Hard refresh: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
   - Or clear browser cache completely
   - Try in incognito/private mode

4. **Check Railway Logs:**
   - Go to Railway → Deployments → View Logs
   - Look for CORS-related errors
   - Verify backend started successfully

---

### Issue: API Calls Going to Wrong URL

**Symptom:** API calls going to `localhost:8000` or wrong domain

**Solutions:**

1. **Verify Vercel Environment Variable:**
   - Go to Vercel → Settings → Environment Variables
   - Check `VITE_API_URL` is set correctly
   - Value should be: `https://ibmdexter-production.up.railway.app/api/v1`

2. **Ensure Frontend Was Redeployed:**
   - Environment variables only apply to NEW deployments
   - Go to Vercel → Deployments
   - Verify deployment happened AFTER adding the variable
   - Check deployment timestamp

3. **Check Browser DevTools:**
   - Open DevTools → Network tab
   - Refresh the page
   - Look at the actual URLs being called
   - They should point to `ibmdexter-production.up.railway.app`

4. **Verify Build Logs:**
   - Go to Vercel → Deployments → View Build Logs
   - Search for `VITE_API_URL`
   - Confirm it's being picked up during build

---

### Issue: 404 Not Found

**Symptom:** API endpoints returning 404 errors

**Solutions:**

1. **Test Backend Directly:**
   ```
   https://ibmdexter-production.up.railway.app/health
   ```
   - Should return JSON with status "ok"
   - If this fails, backend is not running

2. **Check Railway Deployment:**
   - Go to Railway → Deployments
   - Verify latest deployment is successful
   - Check logs for startup errors

3. **Verify API Endpoint Paths:**
   - Frontend expects endpoints at `/api/v1/...`
   - Check that backend is serving at correct paths
   - Test: `https://ibmdexter-production.up.railway.app/api/v1/repositories`

4. **Check Railway Service URL:**
   - Go to Railway → Settings
   - Verify the public URL is correct
   - Should be: `ibmdexter-production.up.railway.app`

---

### Issue: Environment Variable Not Working

**Symptom:** Frontend still using old URL after setting variable

**Solutions:**

1. **Redeploy is Required:**
   - Environment variables only apply to NEW builds
   - You MUST redeploy after adding variables
   - Go to Vercel → Deployments → Redeploy

2. **Check Variable Name:**
   - Must be exactly: `VITE_API_URL`
   - Vite requires `VITE_` prefix
   - Case-sensitive

3. **Check All Environments:**
   - Variable should be set for Production, Preview, AND Development
   - If only set for Production, preview deployments won't work

4. **Verify in Build Logs:**
   - Go to Vercel → Deployments → Build Logs
   - Search for your variable name
   - Confirm it's being used during build

---

### Issue: Backend Not Responding

**Symptom:** Requests timeout or fail to connect

**Solutions:**

1. **Check Railway Service Status:**
   - Go to Railway → Deployments
   - Verify service is running (green status)
   - Check recent logs for errors

2. **Test Health Endpoint:**
   ```
   https://ibmdexter-production.up.railway.app/health
   ```
   - Should respond within 1-2 seconds
   - If timeout, backend is not running

3. **Check Railway Logs:**
   - Look for startup errors
   - Verify database connection succeeded
   - Check for port binding issues

4. **Verify Railway Configuration:**
   - Go to Railway → Settings
   - Check Root Directory is set to `backend`
   - Verify Start Command is correct

---

### Issue: Mixed Content Errors

**Symptom:** Browser blocks requests due to HTTP/HTTPS mismatch

**Solutions:**

1. **Ensure HTTPS Everywhere:**
   - Railway URL should be: `https://ibmdexter-production.up.railway.app`
   - Vercel URL should be: `https://ibm-dexter.vercel.app`
   - Both should use HTTPS (not HTTP)

2. **Check Environment Variable:**
   - Verify `VITE_API_URL` starts with `https://`
   - No `http://` URLs in production

---

## 📱 Testing Endpoints

Test these URLs directly in your browser to verify everything is working:

### Backend Health Check
```
https://ibmdexter-production.up.railway.app/health
```
**Expected Response:**
```json
{
  "status": "ok",
  "service": "IBM Dexter Backend",
  "version": "0.1.0"
}
```

### API Documentation
```
https://ibmdexter-production.up.railway.app/docs
```
**Expected:** FastAPI Swagger UI interface

### Frontend Application
```
https://ibm-dexter.vercel.app
```
**Expected:** IBM Dexter landing page loads

### Frontend Dashboard
```
https://ibm-dexter.vercel.app/app/dashboard
```
**Expected:** Dashboard with data from backend

---

## 📋 Quick Copy-Paste Values

### For Vercel Environment Variables

**Variable Configuration:**
```
Name: VITE_API_URL
Value: https://ibmdexter-production.up.railway.app/api/v1
Environments: Production, Preview, Development (all selected)
```

**Copy-Paste Value:**
```
https://ibmdexter-production.up.railway.app/api/v1
```

---

### For Railway Backend Variables

**Copy-Paste into Railway Raw Editor:**
```bash
DEXTER_CORS_ORIGINS=https://ibm-dexter.vercel.app
DEXTER_FRONTEND_URL=https://ibm-dexter.vercel.app
```

**Individual Values:**

**Variable 1:**
```
Name: DEXTER_CORS_ORIGINS
Value: https://ibm-dexter.vercel.app
```

**Variable 2:**
```
Name: DEXTER_FRONTEND_URL
Value: https://ibm-dexter.vercel.app
```

---

## 🔍 Debugging Tips

### Check Frontend Configuration

1. **View Environment Variables in Build:**
   - Go to Vercel → Deployments → Build Logs
   - Search for `VITE_API_URL`
   - Verify it shows the correct Railway URL

2. **Inspect Network Requests:**
   - Open DevTools → Network tab
   - Filter by "Fetch/XHR"
   - Check the domain of API requests
   - Should be `ibmdexter-production.up.railway.app`

3. **Check Console for Errors:**
   - Open DevTools → Console tab
   - Look for red error messages
   - Common issues: CORS, 404, network errors

### Check Backend Configuration

1. **View Railway Logs:**
   - Go to Railway → Deployments → View Logs
   - Look for CORS configuration messages
   - Verify allowed origins include your frontend URL

2. **Test CORS Headers:**
   - Use browser DevTools → Network tab
   - Check response headers for `Access-Control-Allow-Origin`
   - Should include `https://ibm-dexter.vercel.app`

3. **Verify Environment Variables:**
   - Go to Railway → Variables tab
   - Confirm all CORS variables are set
   - Check for typos or extra spaces

---

## 🎓 Understanding the Configuration

### Why VITE_API_URL?

- **Vite Requirement:** Vite (the build tool) requires environment variables to start with `VITE_`
- **Build-Time Injection:** The value is injected during build, not at runtime
- **Security:** Prevents accidental exposure of server-side secrets

### Why Include /api/v1?

- **API Versioning:** Backend uses `/api/v1` prefix for all endpoints
- **Frontend Expectation:** Frontend code expects this structure
- **Consistency:** Matches the backend's FastAPI router configuration

### Why CORS Configuration?

- **Browser Security:** Browsers block cross-origin requests by default
- **Explicit Permission:** Backend must explicitly allow frontend domain
- **Production Safety:** Prevents unauthorized domains from accessing your API

---

## 📚 Additional Resources

- **Vercel Documentation:** https://vercel.com/docs
- **Vercel Environment Variables:** https://vercel.com/docs/environment-variables
- **Railway Documentation:** https://docs.railway.app/
- **CORS Explained:** https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
- **Vite Environment Variables:** https://vitejs.dev/guide/env-and-mode.html

---

## 🎉 Success Indicators

Your setup is complete when:

✅ **Backend Health Check Returns OK**
```bash
curl https://ibmdexter-production.up.railway.app/health
# Returns: {"status":"ok","service":"IBM Dexter Backend","version":"0.1.0"}
```

✅ **Frontend Loads Without Errors**
- Visit `https://ibm-dexter.vercel.app`
- No console errors
- Dashboard loads data

✅ **API Calls Work**
- Network tab shows requests to Railway backend
- Responses are successful (200 status)
- No CORS errors

✅ **Full Integration**
- Can navigate all pages
- Data loads from backend
- Settings page accessible
- No error messages

---

## 🆘 Still Having Issues?

If you've followed all steps and still experiencing problems:

1. **Double-Check URLs:**
   - Backend: `https://ibmdexter-production.up.railway.app`
   - Frontend: `https://ibm-dexter.vercel.app`
   - No typos, no trailing slashes (except in API URL)

2. **Verify Redeployments:**
   - Both Vercel AND Railway must be redeployed after config changes
   - Check deployment timestamps

3. **Clear Everything:**
   - Clear browser cache
   - Try incognito/private mode
   - Test from different browser

4. **Check Service Status:**
   - Railway service should show "Active"
   - Vercel deployment should show "Ready"
   - Both should have recent successful deployments

5. **Review Logs:**
   - Railway logs for backend errors
   - Vercel build logs for frontend issues
   - Browser console for client-side errors

---

**Made with ❤️ by Bob**