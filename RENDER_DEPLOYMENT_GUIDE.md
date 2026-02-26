# 🚀 RENDER BACKEND DEPLOYMENT - STEP BY STEP GUIDE

## What You'll Get
- Production backend running on cloud (Render)
- URL like: `https://foodis-backend-xxxxx.onrender.com`
- Database connected to PostgreSQL Neon
- 24/7 uptime for your API

---

## ✅ PREREQUISITES
- [ ] GitHub account with Foodis repo pushed
- [ ] Neon PostgreSQL database URL (already have it)
- [ ] Google Maps API key (already have it)

---

## 🎯 STEP 1: CREATE RENDER ACCOUNT

1. Visit: **https://render.com**
2. Click "Get Started" (top right)
3. Choose: "Sign up with GitHub"
4. Authorize Render to access your GitHub
5. Done! You have a Render account

---

## 🎯 STEP 2: CREATE WEB SERVICE

1. In Render dashboard, click: **"New +"** (top right)
2. Select: **"Web Service"**
3. Click: **"Connect GitHub"**

---

## 🎯 STEP 3: SELECT REPOSITORY

1. Under "GitHub repos", find: **"Foodis"** (or your repo name)
2. Click the **"Connect"** button
3. If not listed:
   - Click "Limit GitHub App permissions"
   - Find and select your Foodis repo
   - Authorize

---

## 🎯 STEP 4: CONFIGURE DEPLOYMENT

Fill in these settings:

| Field | Value |
|-------|-------|
| **Name** | foodis-backend |
| **Region** | closest to you (e.g., us-east-1) |
| **Branch** | main |
| **Build Command** | `pip install -r requirements.txt && python manage.py migrate` |
| **Start Command** | `gunicorn foodis.wsgi:application --workers 2 --timeout 120 --bind 0.0.0.0:$PORT` |

### Build Command Breakdown:
```bash
pip install -r requirements.txt  # Install Python packages
&&                              # AND THEN
python manage.py migrate        # Run database migrations
```

### Start Command Breakdown:
```bash
gunicorn foodis.wsgi:application  # Start Django with Gunicorn
--workers 2                        # Use 2 worker processes
--timeout 120                      # 120 second timeout for requests
--bind 0.0.0.0:$PORT             # Listen on all IPs, port given by Render
```

---

## 🎯 STEP 5: ENVIRONMENT VARIABLES

1. Click: **"Advanced"** (below Start Command)
2. Click: **"Add Environment Variable"** (multiple times)

Add these variables:

```
DEBUG                    = False
SECRET_KEY              = strong_random_key_foodis_2026
ALLOWED_HOSTS           = .onrender.com,foodis-gamma.vercel.app,.vercel.app
USE_POSTGRES            = True
DATABASE_URL            = postgresql://neondb_owner:npg_J2BMCAc7xENi@ep-bitter-truth-aipmcaxq-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require
GOOGLE_MAPS_API_KEY     = AIzaSyDTx383dhLLt6etYN5FkxucdkuIyWQbgpA
CSRF_TRUSTED_ORIGINS    = https://foodis-gamma.vercel.app,https://*.vercel.app
CORS_ALLOWED_ORIGINS    = https://foodis-gamma.vercel.app,https://*.vercel.app
```

### Key Variables Explained:

**DEBUG=False**
- Production mode (no sensitive errors shown)

**ALLOWED_HOSTS**
- Which domains can access this API
- Includes Vercel domain + Render domain

**USE_POSTGRES=True**
- Use cloud PostgreSQL (NOT SQLite)

**DATABASE_URL**
- Your Neon PostgreSQL connection string

**GOOGLE_MAPS_API_KEY**
- For location features in your app

**CORS_TRUSTED_ORIGINS**
- Allows Vercel frontend to call Render backend

---

## 🎯 STEP 6: DEPLOY!

1. Scroll to bottom
2. Click: **"Create Web Service"**
3. Watch the deployment happen!

You should see:
```
Building...
Running build command...
Installing dependencies...
Running migrations...
Starting web service...
```

---

## 🎯 STEP 7: GET YOUR BACKEND URL

1. Wait for "Live" status (green check)
2. Your URL appears at the top, looks like:
   ```
   https://foodis-backend-xxxxx.onrender.com
   ```
3. **COPY THIS URL** - you'll need it for Vercel

---

## ✅ VERIFY IT WORKS

Test your backend:

```bash
# On Windows (PowerShell):
curl https://your-url.onrender.com/health/

# Should return: 200 status code
```

Or open in browser:
```
https://your-url.onrender.com/api/client/restaurants/
```

If it works → Status 200 ✅

---

## 🔍 TROUBLESHOOTING

### Status: "Build failed"
- Check the "Logs" tab
- Look for Python errors
- Make sure `requirements.txt` has all packages

### Status: "Starting" for 10+ minutes
- This is normal! Cold start can take time
- Wait a bit longer
- Check logs for errors

### Get 503 error
- Free tier services sleep after 15 min of inactivity
- Hit your URL again → wakes up
- Takes 2-3 minutes to wake

### Get 502 error
- Backend crashed
- Check logs for errors
- Likely a Python exception

### Database connection failed
- Check DATABASE_URL is correct
- Make sure Neon is still working
- Test locally first: `python manage.py shell`

---

## ⏱️ TIMELINE

| Step | Time |
|------|------|
| Sign up to Render | 2 min |
| Create Web Service | 1 min |
| Configure settings | 5 min |
| Deploy | 5-10 min |
| **TOTAL** | **15-20 min** |

---

## 📋 FINAL CHECKLIST

- [ ] Render account created
- [ ] Web Service created
- [ ] Build command set correctly
- [ ] Start command set correctly
- [ ] All 8 environment variables added
- [ ] Deployment started
- [ ] Status shows "Live" (green)
- [ ] Backend URL copied
- [ ] Successfully tested with curl
- [ ] Ready for Vercel configuration

---

## 🎉 NEXT STEPS

Once deployment is complete:

1. Copy your backend URL
2. Go to: https://vercel.com/dashboard
3. Select: foodis-gamma project
4. Settings → Environment Variables
5. Add: `REACT_APP_API_URL = your-backend-url`
6. Trigger Vercel redeploy
7. Test your live app!

---

## 📊 YOUR PRODUCTION SETUP

```
┌─────────────────────────────────────────┐
│         USER'S BROWSER                  │
├─────────────────────────────────────────┤
│  https://foodis-gamma.vercel.app/client │
│  (Frontend on Vercel)                   │
│              ↓                           │
│  REACT_APP_API_URL                      │
│              ↓                           │
│  https://foodis-backend-xxxxx.onrender  │
│  (Backend on Render)                    │
│              ↓                           │
│  PostgreSQL Neon Database               │
└─────────────────────────────────────────┘
```

---

## 💡 PRO TIPS

1. **Monitor your app**: Render Dashboard shows logs in real-time
2. **Custom domain**: Later you can add custom domain (foodis-api.com)
3. **Scale up**: When you have users, upgrade to paid plan
4. **Auto-deploy**: Every Git push to main auto-deploys
5. **Email notifications**: Render can email you on deployment failures

---

## 🆘 QUICK HELP

| Problem | Quick Fix |
|---------|-----------|
| Can't find repo | Grant Render GitHub permissions |
| Env vars not working | Make sure no spaces around = |
| Build fails | Check logs tab for errors |
| Can't set env vars | Click "Advanced" first |
| Status stays "Building" | May take 10+ min, be patient |
| Get 503 after deploy | We'll fix in Vercel config |

---

**Status: Ready to deploy!** ✅

Open https://render.com and start now! 🚀
