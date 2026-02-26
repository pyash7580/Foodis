# Fix Images on Vercel - Complete Solution

## Problem
- Images work on localhost because backend is on `http://localhost:8000`
- On Vercel, frontend has no backend URL, so images fail to load
- Image paths are stored as `/media/...` in database
- These paths need the backend domain (e.g., `https://your-railway-app.railway.app/media/...`)

## Solution: 3 Steps to Fix

### STEP 1: Deploy Backend to Railway (10 minutes)

#### Option A: Using Railway CLI (Fastest)
```bash
# 1. Install Railway CLI from https://docs.railway.app/guides/cli
npm i -g @railway/cli

# 2. Login to Railway
railway login

# 3. From your project root (d:\Foodis), create new project
railway init

# When prompted:
# - Select "Create a new project"
# - Give it a name: "foodis-backend"
# - Select "Python" for environment

# 4. Add environment variables
railway variable set USE_POSTGRES=False
railway variable set SECRET_KEY=your-secret-key
railway variable set DEBUG=False
railway variable set ALLOWED_HOSTS=*.railway.app,foodis-gamma.vercel.app

# 5. Deploy
railway up

# 6. Get your backend URL
railway variables list  # Look for RAILWAY_PUBLIC_URL
# URL will be: https://your-project-abc123.railway.app
```

#### Option B: Using Railway Dashboard (Visual)
1. Go to https://railway.app
2. Click "New Project"
3. Connect your GitHub repository
4. Select the repo
5. Railway auto-detects Django and configures it
6. Add these Environment Variables:
   ```
   USE_POSTGRES=False
   SECRET_KEY=django-insecure-change-me
   DEBUG=False
   ALLOWED_HOSTS=*.railway.app,foodis-gamma.vercel.app
   CORS_ALLOWED_ORIGINS=https://foodis-gamma.vercel.app
   ```
7. Click Deploy
8. Copy Public URL (looks like: `https://foodis-backend-prod-abc.railway.app`)

---

### STEP 2: Update Backend CORS Settings

Edit `d:\Foodis\core\settings.py`:

```python
# Add Vercel frontend to CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://foodis-gamma.vercel.app",
    "https://your-railway-app.railway.app",  # Your backend URL
]

# If using environment variable
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
```

---

### STEP 3: Configure Vercel with Backend URL

After backend is deployed and you have the Railway URL:

#### Using Vercel Dashboard
1. Go to https://vercel.com/dashboard
2. Select your "foodis" project
3. Go to Settings → Environment Variables
4. Add new variable:
   ```
   Name: REACT_APP_API_URL
   Value: https://your-railway-app.railway.app
   ```
5. Click "Save" and "Redeploy"

#### Using Vercel CLI
```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Login
vercel login

# 3. From project root
vercel env add REACT_APP_API_URL
# When prompted for value, paste: https://your-railway-app.railway.app
# Select "Production" when asked for environment

# 4. Redeploy frontend
vercel --prod
```

---

## Quick Copy-Paste Commands

### For Railway CLI:
```bash
# Login and deploy
railway login
railway init  # Select "Create new project" > "Python"
railway variable set USE_POSTGRES=False
railway variable set DEBUG=False
railway variable set ALLOWED_HOSTS=*.railway.app,foodis-gamma.vercel.app
railway up
```

### For Vercel CLI:
```bash
# After you have Railway URL (https://xxx.railway.app)
vercel login
cd d:\Foodis\frontend
vercel env add REACT_APP_API_URL
# Paste: https://xxx.railway.app (replace xxx with actual)
vercel --prod
```

---

## Verification Checklist

- [ ] Railway backend is deployed (check railway.app dashboard - should show "Running")
- [ ] Backend URL is accessible (open in browser: `https://your-url/api/client/`)
- [ ] Vercel environment variable is set (`REACT_APP_API_URL = https://your-url`)
- [ ] Frontend is redeployed on Vercel (check deployments tab)
- [ ] Images load on https://foodis-gamma.vercel.app/client/
- [ ] Restaurant cards display with logos
- [ ] Dish images display correctly

---

## Troubleshooting

### Images still not loading?
1. Check browser console (F12 > Console) for error messages
2. Check Network tab to see if image requests are going to correct URL
3. Verify `REACT_APP_API_URL` is set correctly in Vercel
4. Make sure Railway backend is running

### Railway shows error?
```bash
# Check logs
railway logs

# See all variables
railway variables list
```

### Vercel deployment failed?
```bash
# Check build logs in Vercel dashboard
# Or view locally
vercel build
```

---

## File Locations to Remember
- Backend settings: `d:\Foodis\core\settings.py`
- Frontend config: `d:\Foodis\frontend\src\config.js`
- Frontend env: `d:\Foodis\frontend\.env.production`

