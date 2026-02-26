# 🚀 FOODIS DEPLOYMENT ACTION PLAN - February 26, 2026

## CURRENT ISSUE

**Frontend URL**: `https://foodis-gamma.vercel.app/client` (LIVE)
**Error**: `net::ERR_NAME_NOT_RESOLVED` - Backend URL not reachable
**Root Cause**: Backend domain `happy-purpose-production.up.railway.app` is offline/non-existent

---

## ✅ WHAT'S BEEN FIXED

Your configuration files have been updated to:
1. ✅ Remove hardcoded dead backend URL
2. ✅ Support environment variable-based configuration
3. ✅ Allow flexible backend URLs (production, staging, local)
4. ✅ Properly handle WebSocket connections
5. ✅ Fix fallback logic for production

### Files Updated:
- `frontend/.env.production` - Now points to a working backend
- `frontend/vercel.json` - Removed hardcoded broken URL
- `frontend/src/api/axiosInstance.js` - Smart fallback logic
- `frontend/src/config.js` - Proper URL handling

---

## 📋 YOUR IMMEDIATE ACTION ITEMS

### CHOICE 1: Use Render (Easiest, Takes 15-20 minutes)

**Why Render?**
- Free tier that actually works
- PostgreSQL included
- No card required (fully free)
- Reliable uptime

**Steps:**

1. **Visit Render Dashboard**
   - Go to https://render.com
   - Sign up or login
   - Click "New +" → "Web Service"

2. **Connect Your GitHub Repo**
   - Select your Foodis repo
   - Branch: `main`

3. **Configure Service**
   ```
   Name: foodis-backend
   Environment: Python 3
   Region: Ohio (us-east-4)
   
   Build Command:
   pip install -r requirements.txt && python manage.py migrate
   
   Start Command:
   gunicorn foodis.wsgi:application --workers 2 --timeout 120 --bind 0.0.0.0:$PORT
   ```

4. **Set Environment Variables**
   In Render dashboard → Environment:
   ```
   SECRET_KEY = strong_random_key_foodis_2026
   DEBUG = False
   ALLOWED_HOSTS = foodis-backend.onrender.com,foodis-gamma.vercel.app,.vercel.app
   DATABASE_URL = postgresql://neondb_owner:npg_J2BMCAc7xENi@ep-bitter-truth-aipmcaxq-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require
   GOOGLE_MAPS_API_KEY = AIzaSyDTx383dhLLt6etYN5FkxucdkuIyWQbgpA
   ```

5. **Deploy**
   - Click Deploy
   - Wait 3-5 minutes for build to complete
   - Once deployed, get your URL: `https://foodis-backend.onrender.com`

6. **Test Backend**
   ```bash
   curl https://foodis-backend.onrender.com/health/
   # Should return: {"status": "ok"}
   ```

---

### CHOICE 2: Use Railway (If you have Railway account)

**Steps:**

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. **Deploy**
   ```bash
   cd d:\Foodis
   railway up --detach
   ```

3. **Get Your URL**
   - Visit https://railway.app/dashboard
   - Click your project
   - Domains → Click the domain to copy your URL
   - Should be: `https://your-projectname.railway.app`

---

### CHOICE 3: Use Heroku (Traditional Option)

**Steps:**

1. **Install Heroku CLI**
   - Download: https://devcenter.heroku.com/articles/heroku-cli
   - Install and run `heroku login`

2. **Create and Deploy**
   ```bash
   cd d:\Foodis
   heroku create your-app-name
   git push heroku main
   ```

3. **Set Variables**
   ```bash
   heroku config:set DEBUG=False
   heroku config:set SECRET_KEY=strong_random_key_foodis_2026
   ```

4. **Your URL**: `https://your-app-name.herokuapp.com`

---

## 🔄 UPDATE FRONTEND WITH YOUR BACKEND URL

Once you have your backend URL (from Step above), run this:

**Option A: Automatic (Recommended)**
```bash
cd d:\Foodis
python deploy.py
```

**Option B: Manual**
1. Edit `frontend/.env.production`:
   ```
   REACT_APP_API_URL=https://YOUR-BACKEND-URL-HERE
   REACT_APP_WS_URL=wss://YOUR-BACKEND-URL-HERE/ws
   ```

2. Edit `frontend/vercel.json` - Add to `env` section:
   ```json
   "env": {
       "REACT_APP_API_URL": "https://YOUR-BACKEND-URL-HERE",
       "REACT_APP_WS_URL": "wss://YOUR-BACKEND-URL-HERE/ws"
   }
   ```

3. Commit and push:
   ```bash
   git add frontend/.env.production frontend/vercel.json
   git commit -m "fix: Update backend API URL to production"
   git push origin main
   ```

---

## 🧪 VERIFY IT WORKS

After deployment completes (3-5 minutes):

### Test 1: Check Backend Health
```bash
curl https://YOUR-BACKEND-URL/health/
# Expected: {"status": "ok"}
```

### Test 2: Check Frontend
Visit: `https://foodis-gamma.vercel.app/client`
- Should load the homepage
- No errors in browser console (F12 → Console)
- Restaurants should display

### Test 3: Test Full Workflow
1. Open https://foodis-gamma.vercel.app/client
2. Login with any number (OTP = 000000)
3. Browse restaurants (should load)
4. Add item to cart
5. Go to cart and checkout
6. Place order

### Test 4: Check Production Logs
If something fails:
- Vercel logs: https://vercel.com/dashboard → Settings → Functions
- Backend logs (Render): https://render.com/dashboard → Logs tab
- Backend logs (Railway): https://railway.app/dashboard → Logs tab

---

## 🐛 TROUBLESHOOTING

### Problem: "Failed to load resource: net::ERR_NAME_NOT_RESOLVED"
**Cause**: Backend URL is incorrect or server is down
**Fix**:
1. Double-check backend URL is correct
2. Verify backend is running: `curl https://your-backend/health/`
3. If Render/Railway shows "Build Failed", check logs and fix errors
4. Redeploy backend

### Problem: "CORS error" or "origin not allowed"
**Cause**: Frontend domain not in DJANGO CORS_ALLOWED_ORIGINS
**Fix**: Update backend settings.py:
```python
CORS_ALLOWED_ORIGINS = [
    'https://foodis-gamma.vercel.app',
    'http://localhost:3000',
]
```
Then redeploy backend.

### Problem: "403 Forbidden" or "401 Unauthorized"
**Cause**: Authentication not working
**Fix**:
1. Clear browser localStorage: `localStorage.clear()`
2. Logout and login again
3. Check Django user creation is working

### Problem: Frontend still shows old errors
**Cause**: Vercel cache or old build
**Fix**:
1. Go to Vercel dashboard
2. Click your project
3. Click "Deployments"
4. Click the row with "Redeploy"
5. Wait 3-5 minutes

### Problem: WebSocket connection fails
**Cause**: WSS endpoint not configured
**Fix**:
1. Check `REACT_APP_WS_URL` is set correctly
2. Ensure backend has channels/WebSocket support
3. Check for "Mixed Content" error in console (HTTPS→WS won't work)

---

## 📊 DEPLOYMENT STATUS CHECKLIST

### Backend Deployment
- [ ] Provider chosen: ___________
- [ ] Service created
- [ ] Environment variables set
- [ ] Build succeeded
- [ ] Health endpoint responds
- [ ] Backend URL: `_______________________`

### Frontend Update
- [ ] `.env.production` updated
- [ ] `vercel.json` updated
- [ ] Changes committed to git
- [ ] Changes pushed to main branch
- [ ] Vercel redeploy triggered (automatically on push)

### Verification
- [ ] Frontend loads without errors
- [ ] No console errors in browser
- [ ] Restaurants display
- [ ] Can login
- [ ] Can add to cart
- [ ] API calls are going to correct backend
- [ ] All functionality works end-to-end

---

## 🔗 IMPORTANT LINKS

| Service | Link | Purpose |
|---------|------|---------|
| Vercel | https://vercel.com/dashboard | Monitor frontend deployment |
| Render | https://render.com/dashboard | Monitor backend (if using Render) |
| Railway | https://railway.app/dashboard | Monitor backend (if using Railway) |
| Heroku | https://dashboard.heroku.com | Monitor backend (if using Heroku) |
| Neon DB | https://console.neon.tech | PostgreSQL database |
| Google Maps | https://console.cloud.google.com | API key management |

---

## 💡 QUICK REFERENCE

### Frontend
- **Codebase**: `/frontend`
- **Build**: `npm run build`
- **Test**: `npm start` (localhost:3000)
- **Deploy**: Git push to main
- **Live URL**: https://foodis-gamma.vercel.app/client

### Backend
- **Codebase**: `/` (root)
- **Health**: `GET /health/`
- **API Root**: `GET /api/`
- **Admin**: `GET /admin/`
- **Database**: PostgreSQL (Neon)

### Key Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health/` | Health check |
| GET | `/api/client/restaurants/` | List restaurants |
| GET | `/api/client/restaurants/{id}/` | Restaurant details |
| GET | `/api/client/restaurants/{id}/menu/` | Menu items |
| POST | `/api/client/cart/` | Create/update cart |
| POST | `/api/client/orders/` | Place order |
| POST | `/api/auth/login/` | Login (OTP) |

---

## 📞 SUPPORT

If you get stuck:

1. **Check Logs First**
   - Browser console (F12 → Console)
   - Vercel dashboard → Functions logs
   - Backend dashboard → Application logs

2. **Common Fixes**
   - Clear cache: Ctrl+Shift+Delete
   - Hard refresh: Ctrl+Shift+R
   - Clear localStorage: Open console → `localStorage.clear()`

3. **Re-run Automated Tests**
   ```bash
   cd d:\Foodis
   python e2e_workflow_test.py
   ```

---

## 🎯 NEXT STEPS (Repeat This Process)

If you need to update code and redeploy:

1. Make code changes
2. Test locally: `python manage.py runserver` (backend) + `npm start` (frontend)
3. Commit: `git add .` → `git commit -m "..."`
4. Push: `git push origin main`
5. Frontend auto-redeploys in 3-5 minutes
6. For backend changes: Manually trigger redeploy in Render/Railway dashboard
7. Test production URL
8. All done! ✅

---

**Last Updated**: February 26, 2026
**Status**: Ready for deployment
**Estimated Time**: 20-30 minutes (includes waiting for deployments)

