# FOODIS COMPLETE DEPLOYMENT GUIDE - February 2026

## 🎯 CURRENT SITUATION
- **Frontend**: Deployed to `https://foodis-gamma.vercel.app/client`
- **Backend URL**: Hardcoded to `https://happy-purpose-production.up.railway.app` (NOT RESPONDING)
- **Error**: `net::ERR_NAME_NOT_RESOLVED` - Backend domain is not resolvable
- **Status**: Frontend is up, but cannot communicate with backend

---

## 🔧 SOLUTION OVERVIEW

You need to:
1. **Deploy working backend** (Setup Railway or use Render)
2. **Update frontend environment variables** with correct backend URL
3. **Redeploy frontend to Vercel**
4. **Verify end-to-end connectivity**

---

## ⚡ QUICK FIX (Complete in 30 minutes)

### Step 1: Choose Backend Provider (Pick ONE)

#### OPTION A: Railway (Recommended if alive)
```bash
# Prerequisites
npm install -g @railway/cli
# Login to Railway from CLI
railway login

# Deploy backend
cd d:\Foodis
railway up --detach
# Get your Railway URL: https://railway.app/dashboard
# Your backend URL will be shown after deployment
```

#### OPTION B: Render (More stable free tier)
```bash
# 1. Go to https://render.com
# 2. Create account and connect GitHub
# 3. Create new Web Service
# 4. Select your Foodis repo
# 5. Use these settings:
#    - Runtime: Python 3.11
#    - Build command: pip install -r requirements.txt && python manage.py migrate
#    - Start command: gunicorn foodis.wsgi:application --workers 2 --bind 0.0.0.0:$PORT
#    - Environment variables: See below
```

### Step 2: Set Backend Environment Variables

For your chosen provider (Railway or Render), set these variables:

```
SECRET_KEY=strong_random_key_foodis_2026
DEBUG=False
ALLOWED_HOSTS=your-domain.railway.app,your-domain.onrender.com,foodis-gamma.vercel.app,.vercel.app,localhost,127.0.0.1
DATABASE_URL=postgresql://neondb_owner:npg_J2BMCAc7xENi@ep-bitter-truth-aipmcaxq-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
REDIS_URL=your-redis-url-here (optional - local cache will work without it)
GOOGLE_MAPS_API_KEY=AIzaSyDTx383dhLLt6etYN5FkxucdkuIyWQbgpA
DEBUG=False
```

### Step 3: Get Your Backend URL

After deployment completes:
- **Railway**: Go to https://railway.app → Your project → Domain → Copy the URL
- **Render**: Go to https://render.com → Your service → Copy the URL

Example: `https://your-backend-name.railway.app` or `https://your-backend-name.onrender.com`

### Step 4: Update Frontend Configuration

1. Navigate to frontend directory
```bash
cd d:\Foodis\frontend
```

2. Create/Update `.env.production`:
```
REACT_APP_API_URL=https://YOUR-BACKEND-URL-HERE
REACT_APP_WS_URL=wss://YOUR-BACKEND-URL-HERE/ws
REACT_APP_GOOGLE_MAPS_API_KEY=AIzaSyDTx383dhLLt6etYN5FkxucdkuIyWQbgpA
GENERATE_SOURCEMAP=false
CI=false
```

3. Update `vercel.json`:
```json
{
    "version": 2,
    "buildCommand": "npm run build",
    "outputDirectory": "build",
    "rewrites": [
        {
            "source": "/(.*)",
            "destination": "/index.html"
        }
    ],
    "env": {
        "REACT_APP_API_URL": "https://YOUR-BACKEND-URL-HERE",
        "REACT_APP_WS_URL": "wss://YOUR-BACKEND-URL-HERE/ws",
        "DISABLE_ESLINT_PLUGIN": "true",
        "SKIP_PREFLIGHT_CHECK": "true",
        "GENERATE_SOURCEMAP": "false"
    }
}
```

### Step 5: Deploy Frontend to Vercel

```bash
cd d:\Foodis
# Make sure you have changes staged
git add frontend/.env.production frontend/vercel.json
git commit -m "fix: Update backend API URL for production deployment"
git push origin main

# Vercel will auto-deploy
# Monitor at: https://vercel.com/dashboard
```

### Step 6: Verify Deployment

Test both locally and on production:

```bash
# LOCAL TEST
cd d:\Foodis\frontend
npm start
# Visit http://localhost:3000/client
# Should show restaurants (no errors in console)

# PRODUCTION TEST
# Visit https://foodis-gamma.vercel.app/client
# Should show restaurants without errors
# Check browser console for errors
```

---

## 🔍 TROUBLESHOOTING

### Issue: "Failed to load resource: net::ERR_NAME_NOT_RESOLVED"
**Cause**: Backend domain not resolvable (DNS issue or service down)
**Fix**: 
1. Verify backend was deployed successfully and is running
2. Check the domain is correct in `vercel.json` and `.env.production`
3. Test backend directly: `curl https://YOUR-BACKEND-URL/health/`
4. If backend is down, redeploy it

### Issue: "Failed to load resource: net::ERR_BLOCKED_BY_CLIENT"
**Cause**: CSP policy or browser extension blocking requests
**Fix**:
1. Disable browser extensions (especially ad blockers)
2. Check browser console for CSP violations
3. Verify `CORS_ALLOWED_ORIGINS` includes frontend domain in Django settings

### Issue: Build fails on Vercel
**Cause**: Missing environment variables
**Fix**:
1. Go to Vercel Dashboard → Project → Settings → Environment Variables
2. Add: `REACT_APP_API_URL` and `REACT_APP_WS_URL`
3. Trigger redeploy (git push)

### Issue: "Cannot GET /client"
**Cause**: React Router not configured for Vercel
**Fix**: Ensure `vercel.json` has the rewrites rule (included above)

---

## 📋 COMPLETE CHECKLIST

- [ ] Choose backend provider (Railway or Render)
- [ ] Deploy backend
- [ ] Get backend URL
- [ ] Update frontend `.env.production`
- [ ] Update frontend `vercel.json`
- [ ] Test locally
- [ ] Commit and push changes
- [ ] Wait for Vercel deployment (3-5 minutes)
- [ ] Test production URL
- [ ] Verify browser console is clean
- [ ] Check both Desktop and Mobile

---

## 🚀 TESTING SCRIPT

```bash
# Run this after deployment to verify everything works
cd d:\Foodis
python e2e_workflow_test.py

# Should pass:
# ✅ Backend health check
# ✅ Client login
# ✅ Browse restaurants
# ✅ Add to cart
# ✅ Place order
```

---

## 📝 DEPLOYMENT RECORD

Record your deployment here for future reference:

**Backend Deployment:**
- Provider: ☐ Railway  ☐ Render  ☐ Other
- URL: `_____________________________`
- Deployed on: __________ (date)
- Status: ☐ Running  ☐ Failed

**Frontend Deployment:**
- URL: `https://foodis-gamma.vercel.app/client`
- Environment Variables Updated: ☐ Yes  ☐ No
- Last Deployed: __________ (date)

---

## 🔗 USEFUL LINKS

- Railway Dashboard: https://railway.app/dashboard
- Render Dashboard: https://render.com/dashboard
- Vercel Dashboard: https://vercel.com/dashboard
- Neon Database: https://console.neon.tech
- Django Admin: `https://YOUR-BACKEND-URL/admin`

---

## 💡 TIPS

1. **Local Testing is Critical**: Always test locally before deploying
2. **Environment Variables**: Keep them secret - never commit to git
3. **Backend Health Check**: Add monitoring to `https://YOUR-BACKEND-URL/health/`
4. **Logs**: Check deployment logs for errors (Vercel, Railway, Render dashboards)
5. **CORS Issues**: If API calls fail, check CORS_ALLOWED_ORIGINS in backend settings

---

**Document Created**: February 26, 2026
**Last Updated**: February 26, 2026
