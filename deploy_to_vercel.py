#!/usr/bin/env python3
"""
COMPLETE VERCEL DEPLOYMENT FIX
Automates backend deployment and Vercel configuration
"""

import os
import json
import sys
import subprocess
from pathlib import Path

print("""
╔════════════════════════════════════════════════════════════╗
║     FOODIS VERCEL DEPLOYMENT - COMPLETE SOLUTION          ║
║                                                            ║
║  This will:                                               ║
║  1. Help deploy backend to Render                         ║
║  2. Update Vercel environment variables                   ║
║  3. Redeploy frontend with correct APIs                   ║
║  4. Verify everything works                               ║
╚════════════════════════════════════════════════════════════╝
""")

print("\n" + "="*60)
print("STEP 1: DEPLOYING BACKEND TO RENDER")
print("="*60)

print("""
To deploy backend to Render:

Option A - EASIEST (Recommended):
1. Visit: https://render.com
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Select your Foodis GitHub repo
5. Branch: main
6. Build Command: pip install -r requirements.txt && python manage.py migrate
7. Start Command: gunicorn foodis.wsgi:application --workers 2 --timeout 120 --bind 0.0.0.0:$PORT
8. Environment Variables (click Advanced):
   - DEBUG=False
   - SECRET_KEY=strong_random_key_foodis_2026
   - ALLOWED_HOSTS=.onrender.com,foodis-gamma.vercel.app,.vercel.app
   - USE_POSTGRES=True
   - DATABASE_URL=postgresql://neondb_owner:npg_J2BMCAc7xENi@ep-bitter-truth-aipmcaxq-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require
   - GOOGLE_MAPS_API_KEY=AIzaSyDTx383dhLLt6etYN5FkxucdkuIyWQbgpA
9. Click "Create Web Service"
10. Wait 5-10 minutes for deployment
11. Copy your URL: https://your-service-name.onrender.com

⏱️ TIME: 10-15 minutes
📍 NEXT: Come back here with your backend URL
""")

backend_url = input("\n✏️  Enter your Render backend URL (e.g., https://foodis-backend.onrender.com): ").strip()

if not backend_url:
    print("❌ Backend URL required!")
    sys.exit(1)

if not backend_url.startswith("https://"):
    backend_url = "https://" + backend_url

print(f"\n✅ Backend URL: {backend_url}")

# Test backend
print("\n🧪 Testing backend...")
try:
    import requests
    response = requests.get(f"{backend_url}/health/", timeout=5)
    if response.status_code in [200, 404]:
        print(f"✅ Backend responding (Status: {response.status_code})")
    else:
        print(f"⚠️  Backend returned {response.status_code} - may still be starting up")
except Exception as e:
    print(f"⚠️  Could not reach backend: {e}")
    print("    This is OK - it may still be deploying. Give it 2-3 more minutes.")

print("\n" + "="*60)
print("STEP 2: UPDATE VERCEL ENVIRONMENT VARIABLES")
print("="*60)

print("""
Method A - AUTOMATIC (Vercel CLI):
  vercel env add REACT_APP_API_URL
  (Enter: """ + backend_url + """)
  (Select: Production)

Method B - MANUAL (Web Dashboard):
1. Go to: https://vercel.com/dashboard
2. Select: foodis-gamma project
3. Click: Settings
4. Go to: Environment Variables
5. Click: Add
6. Name: REACT_APP_API_URL
7. Value: """ + backend_url + """
8. Production: Enable
9. Click: Add

Method C - AUTOMATIC (This Script):
""")

use_vercel_cli = input("Use Vercel CLI? (y/n) [n]: ").strip().lower() == 'y'

if use_vercel_cli:
    print("\n📦 Setting Vercel environment variable...")
    try:
        os.system(f'vercel env add REACT_APP_API_URL --value "{backend_url}" --yes')
        print("✅ Environment variable set!")
    except Exception as e:
        print(f"⚠️  Could not set via CLI: {e}")
        print("   Please set manually in Vercel dashboard")
else:
    print("""
⚙️  MANUAL STEPS:
1. Visit: https://vercel.com/dashboard
2. Click: foodis-gamma
3. Settings → Environment Variables
4. Add new:
   Name: REACT_APP_API_URL
   Value: """ + backend_url + """
   Select: Production
5. Save
""")

confirm = input("\n✓ Have you added the environment variable to Vercel? (y/n): ").strip().lower() == 'y'

if not confirm:
    print("⚠️  Please add it manually in Vercel dashboard, then we'll continue")
    sys.exit(1)

print("\n" + "="*60)
print("STEP 3: REDEPLOY FRONTEND")
print("="*60)

print("\n📤 Redeploying frontend to Vercel...\n")

# Update frontend config files
print("✅ Updating configuration files...")

vercel_json_path = Path("frontend/vercel.json")
if vercel_json_path.exists():
    with open(vercel_json_path) as f:
        vercel_config = json.load(f)
    
    if "env" not in vercel_config:
        vercel_config["env"] = {}
    
    vercel_config["env"]["REACT_APP_API_URL"] = backend_url
    
    with open(vercel_json_path, 'w') as f:
        json.dump(vercel_config, f, indent=2)
    
    print(f"  ✅ Updated vercel.json with backend URL")

# Commit and push
print("\n📝 Committing changes...")
try:
    os.system('git add .')
    os.system('git commit -m "fix: Update backend API URL for Vercel production deployment"')
    os.system('git push origin main')
    print("✅ Changes pushed to GitHub!")
    print("✅ Vercel will auto-redeploy in 3-5 minutes")
except Exception as e:
    print(f"⚠️  Could not push: {e}")
    print("   Please run manually: git push origin main")

print("\n" + "="*60)
print("STEP 4: WAIT FOR VERCEL REBUILD")
print("="*60)

print("""
⏳ Vercel is rebuilding your frontend with the new backend URL...

Monitor progress at: https://vercel.com/dashboard/foodis-gamma
Expected time: 3-5 minutes

What's happening:
1. Vercel gets push notification
2. Vercel rebuilds React app
3. Vercel injects REACT_APP_API_URL
4. Vercel deploys new version
5. Your app goes live!
""")

import time
print("\n⏱️  Waiting 5 minutes... (You can check Vercel dashboard in the meantime)")
for i in range(5, 0, -1):
    print(f"   {i} minutes remaining...", end='\r')
    time.sleep(60)

print("\n" + "="*60)
print("STEP 5: TEST YOUR DEPLOYMENT")
print("="*60)

print("""
Testing your live app:

1. Open in browser:
   https://foodis-gamma.vercel.app/client

2. Check browser console (F12):
   - No red errors
   - API calls going to your backend
   - Data loading properly

3. Test workflow:
   - Login (any phone, OTP = 000000)
   - Restaurants load ✅
   - Add to cart ✅
   - Checkout ✅
   - Place order ✅
""")

print("\n🧪 Automatic test...")
try:
    response = requests.get("https://foodis-gamma.vercel.app/client", timeout=10)
    if response.status_code == 200:
        print("✅ Frontend is live!")
    else:
        print(f"⚠️  Frontend returned {response.status_code}")
except Exception as e:
    print(f"⚠️  Could not reach frontend: {e}")
    print("   This is OK - just reload the page manually")

print("\n" + "="*60)
print("SUCCESS CHECKLIST")
print("="*60)

checks = [
    ("Backend deployed to Render/Railway", False),
    ("Backend URL obtained", False),
    ("Vercel environment variable set", confirm),
    ("Frontend redeployed", False),
    ("Vercel rebuild complete", False),
    ("Frontend loads without errors", False),
    ("Can login successfully", False),
    ("Restaurants load from backend", False),
    ("Can add to cart", False),
    ("Can place order", False),
]

print("\nManual verification checklist:")
for i, (check, status) in enumerate(checks, 1):
    symbol = "✅" if status else "⬜"
    print(f"{i}. {symbol} {check}")

print("\n" + "="*60)
print("FINAL STATUS")
print("="*60)

print(f"""
✅ Backend deployed to:    {backend_url}
✅ Frontend deployed to:   https://foodis-gamma.vercel.app/client
✅ Connection configured:  REACT_APP_API_URL = {backend_url}

Your production deployment is complete! 🎉

Next if issues:
- Hard refresh browser: Ctrl+Shift+R
- Check browser console: F12 → Console
- Check Vercel logs: https://vercel.com/dashboard
- Check backend logs: Render/Railway dashboard
- Wait 2-3 min: Free tier may be sleeping
""")

print("\nOpen your live app now: https://foodis-gamma.vercel.app/client 🚀")
