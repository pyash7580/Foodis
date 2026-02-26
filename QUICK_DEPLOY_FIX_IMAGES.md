# Quick Deploy + Fix Images - 15 Minutes

## The Problem
- Images work on localhost (port 3000) because backend is on port 8000
- On Vercel, backend is completely missing - images can't load
- Need to deploy backend to cloud (Railway is fastest)

## The Solution: 3 Simple Steps

### ✅ Step 1: Deploy Backend to Railway (10 min)

Open PowerShell and paste these commands one by one:

```powershell
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway (browser will open)
railway login
```

Then in VS Code terminal:
```powershell
cd d:\Foodis

# Initialize Railway project
railway init

# WHEN PROMPTED:
# → Create a new project
# → Name: "foodis-backend"  
# → Environment: Python

# Set environment variables for production
railway variable set USE_POSTGRES=False
railway variable set DEBUG=False
railway variable set ALLOWED_HOSTS=*.railway.app,foodis-gamma.vercel.app

# Deploy!
railway up
```

**Wait for deployment to finish** - you'll see a success message.

### 📍 Get Your Railway URL

```powershell
railway variables list
```

Look for something like: `https://foodis-xxxxx.railway.app`

Copy this URL - you'll need it in next step!

---

### ✅ Step 2: Configure Vercel with Backend URL (3 min)

**Option A: Using Vercel Dashboard (Easier)**

1. Go to https://vercel.com/dashboard
2. Click "foodis-gamma" project
3. Go to **Settings → Environment Variables**
4. Click **"Add"**
   - Name: `REACT_APP_API_URL`
   - Value: `https://your-railway-url.railway.app` (paste your Railway URL from Step 1)
   - Check "Production"
   - Click **"Save"**
5. Go to **Deployments**
6. Click the **three dots** on latest deployment
7. Click **"Redeploy"**

Wait for redeployment (~2 minutes)

**Option B: Using Vercel CLI (Faster)**

```powershell
# Install Vercel CLI
npm install -g vercel

# Login (browser will open)
vercel login

# Add environment variable
# Paste your Railway URL when prompted
vercel env add REACT_APP_API_URL

# Redeploy with new env var
cd d:\Foodis\frontend
vercel --prod
```

---

### ✅ Step 3: Test Images (2 min)

1. Open https://foodis-gamma.vercel.app/client/
2. You should see restaurant logos
3. Click a restaurant → you should see dish images
4. If images don't show:
   - Press **Ctrl+Shift+Del** to clear cache
   - Press **Ctrl+Shift+R** to hard refresh
   - Open **F12** → **Console** to see errors

---

## Troubleshooting

### "Images still don't show"
```
→ Make sure Railway backend is running
→ Go to railway.app/dashboard
→ Your "foodis-backend" project should show "Running"
→ Click it and check the "Deploy" log has no errors
```

### "Railway deployment is taking too long"
```
→ Normal! Can take 3-5 minutes first time
→ Check at https://railway.app/dashboard
→ You'll see the logs
```

### "Can't find my Railway URL"
```
→ Go to https://railway.app/dashboard
→ Click "foodis-backend" project
→ Look for "Public URL" section
→ That's your Railway URL!
```

---

## Success Checklist

- [ ] Railway backend deployed (shows "Running" in dashboard)
- [ ] Vercel has `REACT_APP_API_URL` set (Settings → Environment Variables)
- [ ] Frontend redeployed on Vercel  
- [ ] Images show on https://foodis-gamma.vercel.app/client/
- [ ] Clicking restaurants shows menu with images
- [ ] Orders can be placed with images visible

---

## Your URLs

- **Frontend:** https://foodis-gamma.vercel.app
- **Backend:** https://your-railway-app.railway.app (get from Step 1)
- **Admin:** https://foodis-gamma.vercel.app/admin

Paste your Railway URL here after Step 1:
```
_______________________________________
```

