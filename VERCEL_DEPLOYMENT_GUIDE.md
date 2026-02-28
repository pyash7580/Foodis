# Deploy Foodis Frontend to Vercel - Step by Step Guide

## Method 1: Using Vercel Dashboard (Recommended - Easiest)

### Step 1: Go to Vercel
1. Open your browser and go to: **https://vercel.com**
2. Click **"Login"** or **"Sign Up"** (if you don't have an account)
3. Sign in with your **GitHub account**

### Step 2: Import Your Project
1. Once logged in, click **"Add New..."** button (top right)
2. Select **"Project"**
3. You'll see "Import Git Repository"
4. Find your **Foodis** repository in the list
5. Click **"Import"** next to it

### Step 3: Configure Project Settings

**Framework Preset:**
- Select: **Create React App**

**Root Directory:**
- Click **"Edit"**
- Enter: `frontend`
- This tells Vercel your React app is in the frontend folder

**Build and Output Settings:**
- Build Command: `npm run build` (should be auto-detected)
- Output Directory: `build` (should be auto-detected)
- Install Command: `npm install` (should be auto-detected)

### Step 4: Add Environment Variables
Click **"Environment Variables"** section and add:

| Name | Value |
|------|-------|
| `REACT_APP_API_URL` | `https://happy-purpose-production.up.railway.app` |
| `REACT_APP_GOOGLE_MAPS_API_KEY` | `AIzaSyDTx383dhLLt6etYN5FkxucdkuIyWQbgpA` |

**Important:** Make sure to check all three environments:
- ✅ Production
- ✅ Preview
- ✅ Development

### Step 5: Deploy!
1. Click **"Deploy"** button
2. Wait 2-3 minutes for the build to complete
3. You'll see a success screen with your deployment URL

### Step 6: Get Your URL
Once deployed, you'll get a URL like:
- `https://foodis-xxxxx.vercel.app`

You can also set a custom domain later if you want.

---

## Method 2: Using Vercel CLI (Alternative)

If you prefer command line:

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Login to Vercel
```bash
vercel login
```

### Step 3: Deploy from Frontend Directory
```bash
cd frontend
vercel
```

Follow the prompts:
- Set up and deploy? **Y**
- Which scope? Select your account
- Link to existing project? **N**
- What's your project's name? **foodis**
- In which directory is your code located? **./`** (current directory)
- Want to override settings? **Y**
  - Build Command: `npm run build`
  - Output Directory: `build`
  - Development Command: `npm start`

### Step 4: Add Environment Variables
```bash
vercel env add REACT_APP_API_URL
# Enter: https://happy-purpose-production.up.railway.app

vercel env add REACT_APP_GOOGLE_MAPS_API_KEY
# Enter: AIzaSyDTx383dhLLt6etYN5FkxucdkuIyWQbgpA
```

### Step 5: Deploy to Production
```bash
vercel --prod
```

---

## Troubleshooting

### Build Fails
**Issue:** Build fails with errors

**Solution:**
1. Check the build logs in Vercel dashboard
2. Make sure all dependencies are in `package.json`
3. Try building locally first: `cd frontend && npm run build`

### Environment Variables Not Working
**Issue:** API calls fail or app doesn't work

**Solution:**
1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Make sure `REACT_APP_API_URL` is set correctly
3. Redeploy: Deployments → Click "..." → Redeploy

### 404 Errors on Routes
**Issue:** Direct URLs show 404

**Solution:**
Already configured in `vercel.json`:
```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/" }
  ]
}
```

If still having issues, make sure `vercel.json` is in the `frontend` directory.

---

## After Deployment

### Test Your Application
1. Visit your Vercel URL
2. Test login functionality
3. Test restaurant browsing
4. Test cart and checkout
5. Make sure images load correctly

### Set Up Custom Domain (Optional)
1. Go to Vercel Dashboard → Your Project → Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions

### Enable Automatic Deployments
Already configured! Every time you push to GitHub:
- Push to `main` branch → Deploys to Production
- Push to other branches → Creates Preview deployments

---

## Quick Reference

**Vercel Dashboard:** https://vercel.com/dashboard

**Your Backend (Railway):** https://happy-purpose-production.up.railway.app

**Environment Variables Needed:**
- `REACT_APP_API_URL` = Railway backend URL
- `REACT_APP_GOOGLE_MAPS_API_KEY` = Your Google Maps API key

**Root Directory:** `frontend`

**Build Command:** `npm run build`

**Output Directory:** `build`

---

## Success Checklist

- [ ] Logged into Vercel
- [ ] Imported GitHub repository
- [ ] Set root directory to `frontend`
- [ ] Added environment variables
- [ ] Clicked Deploy
- [ ] Deployment succeeded
- [ ] Tested the live URL
- [ ] Application works correctly

---

**Need Help?** Check the Vercel documentation: https://vercel.com/docs

Good luck with your deployment! 🚀
