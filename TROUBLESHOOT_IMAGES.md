# Images Not Showing - Troubleshooting Guide

## Why Images Aren't Showing on Vercel

When you access `https://foodis-gamma.vercel.app/client/`, images fail to load because:

1. **Image URLs stored in database**: They look like `/media/restaurant/abc123.jpg`
2. **These are relative paths**: They need the backend domain prepended
3. **Backend not deployed**: Vercel frontend has no way to reach your local backend
4. **Result**: Browser tries to load `https://foodis-gamma.vercel.app/media/...` (doesn't exist)

## The Fix: 3 Components

### Component 1: Deploy Backend to Railway

**Your backend must be accessible on the internet**

```
Local: http://localhost:8000  ❌ Not accessible from Vercel
Cloud: https://xxx.railway.app ✅ Accessible from anywhere
```

**Steps:**
1. Go to https://railway.app
2. Sign up (free account)
3. Connect your GitHub
4. Create new project from your Foodis repo
5. Railway auto-deploys
6. Get your public URL: `https://xxx.railway.app`

**Check it's working:**
```bash
curl https://xxx.railway.app/api/client/
# Should return JSON data, status 200
```

### Component 2: Configure Frontend URLs

**The frontend needs to know where the backend is**

In `d:\Foodis\frontend\src\config.js`:
- On localhost → uses proxy (no change needed)
- On Vercel → reads `REACT_APP_API_URL` environment variable

When images are loaded, they get prefixed:
```
Image path in DB: /media/restaurant/logo.jpg
+ API_BASE_URL: https://xxx.railway.app
= Full URL: https://xxx.railway.app/media/restaurant/logo.jpg ✅
```

**Code is already updated** in:
- `ImageWithFallback.js` - adds API base to relative paths
- `RestaurantCard.js` - same logic implemented
- Both components now properly construct full image URLs

### Component 3: Vercel Environment Variable

**Vercel needs to inject the backend URL during build**

```
REACT_APP_API_URL = https://xxx.railway.app
```

This tells React where the backend is when building for production.

**How to set it:**
1. Go to Vercel Dashboard
2. Select "foodis-gamma" project
3. Settings → Environment Variables
4. Add: `REACT_APP_API_URL = https://your-railway-url`
5. Make sure it's for "Production"
6. Redeploy frontend

## Testing

### Test 1: Check Backend is Reachable
```bash
# Should return data (200 OK)
curl https://xxx.railway.app/api/client/restaurants/

# Try on your computer
curl https://your-railway-url.railway.app/api/client/
```

### Test 2: Check Frontend Gets Environment Variable
```javascript
// Open browser console (F12) and paste:
console.log('API Base URL:', REACT_APP_API_URL)
// Should show: https://xxx.railway.app
```

### Test 3: Check Image Loading
1. Open Vercel site
2. Open F12 → Network tab
3. Filter by images
4. Click a restaurant
5. Watch image requests:
   - Should be `https://xxx.railway.app/media/...`
   - Status should be 200
   - Image should appear

### Test 4: Check Console for Errors
```
F12 → Console → look for red errors
Should show no 404 or CORS errors
```

## Common Issues & Fixes

### Issue 1: Images still show broken icon

**Cause:** Railway backend URL not in Vercel environment

**Fix:**
```
1. Go to Vercel dashboard
2. Settings → Environment Variables  
3. Verify REACT_APP_API_URL is set
4. If not there, add it
5. Click "Redeploy" on Deployments tab
```

### Issue 2: "Failed to load image" in console

**Cause:** Image path is wrong, or backend not running

**Fix:**
```
1. Check Network tab in F12
2. Look at full URL of failed image
3. It should be: https://xxx.railway.app/media/...
4. Try that URL in browser directly
5. If it fails, Railway backend has issue
```

### Issue 3: CORS Error in Console

**Cause:** Backend not allowing requests from Vercel domain

**Fix:**
```
1. Update d:\Foodis\foodis\settings.py
2. Add to CORS_ALLOWED_ORIGINS:
   'https://foodis-gamma.vercel.app'
3. Commit and push
4. Railway redeploys automatically
5. Redeploy Vercel frontend
```

### Issue 4: WhiteNoise Error (Static Files)

**Cause:** Backend not serving static media files

**Fix:**
```
Check foodis/settings.py:
- MEDIA_URL should be '/media/'
- MEDIA_ROOT should be pointing to media folder
- WhiteNoise middleware should be installed
```

## CLI Commands Reference

### Railway - Deploy Backend
```bash
# Install Railway
npm install -g @railway/cli

# Login
railway login

# Initialize project (in project root)
railway init

# Set environment variables
railway variable set USE_POSTGRES=False
railway variable set DEBUG=False
railway variable set ALLOWED_HOSTS=*.railway.app,foodis-gamma.vercel.app

# Deploy
railway up

# Get URL
railway variables list
# Look for the public URL
```

### Vercel - Set Environment & Redeploy
```bash
# Install Vercel
npm install -g vercel

# Login
vercel login

# Add environment variable (from project root)
vercel env add REACT_APP_API_URL
# Enter: https://your-railway-url.railway.app

# Redeploy
cd frontend
vercel --prod
```

## File Locations

Component | File | What it does
----------|------|----------
Image with relative paths | `frontend/src/components/ImageWithFallback.js` | Adds API base URL to `/media/...` paths
Restaurant images | `frontend/src/components/RestaurantCard.js` | Uses `getImageSrc()` to construct full URLs
Dish images | `frontend/src/components/DishCard.js` | Uses `ImageWithFallback` component
Config | `frontend/src/config.js` | Provides `API_BASE_URL` from environment
Backend CORS | `foodis/settings.py` | Allows requests from Vercel domain
Backend media | `media/` folder (root) | Stores uploaded images

## Decision Tree

```
Images showing on localhost:3000?
├─ YES → Configure Vercel environment variable
│        └─ REACT_APP_API_URL = http://localhost:8000
│
└─ NO → Fix local backend first
       ├─ Start backend: python manage.py runserver
       ├─ Check migrations: python manage.py migrate
       ├─ Check media folder exists: ls media/
       └─ Check database has data

Images not showing on Vercel?
├─ Check Railway URL is accessible
│  └─ curl https://xxx.railway.app/api/client/
│
├─ Check Vercel env variable exists
│  └─ REACT_APP_API_URL = https://xxx.railway.app
│
├─ Check frontend is redeployed
│  └─ Should show "Ready" in Vercel Deployments
│
├─ Check browser for errors (F12)
│  ├─ Look for 404 errors on images
│  ├─ Look for CORS errors
│  └─ Look for timeout errors
│
└─ Check image URL in Network tab
   └─ Should start with https://xxx.railway.app/media/
```

## Success Indicators

✅ All images show on Vercel
✅ No 404 or CORS errors in console
✅ Images have correct full URLs in Network tab
✅ Restaurant pages load quickly
✅ Dishes show with proper sizing
✅ Logos appear on restaurant cards

## Need Help?

Check these files in order:

1. **Frontend runs locally?**
   - `d:\Foodis\QUICK_DEPLOY_FIX_IMAGES.md` - Quick 15 min fix
   
2. **Backend not deployed?**
   - `d:\Foodis\FIX_IMAGES_AND_DEPLOY.md` - Complete deployment guide
   
3. **Errors after deployment?**
   - `d:\Foodis\deploy_complete.py` - Automated deployment script
   - Run: `python deploy_complete.py`

4. **Still stuck?**
   - Check `foodis/settings.py` for CORS
   - Check `frontend/.env.production` for env vars
   - Check Railway dashboard for backend logs
   - Check Vercel dashboard for build logs

