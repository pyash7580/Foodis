# Transfer Local Data to Railway Database

## Step 1: Export Local Data

Run this command in your local project:

```bash
python transfer_to_railway.py
```

This will create `railway_data.json` with all your local data.

## Step 2: Link to Backend Service (Important!)

Make sure you link to the **foodis-backend** service, NOT the database:

```bash
railway link
```

Select:
- Workspace: MR YASH's Projects
- Project: soothing-passion
- Environment: production
- Service: **foodis-backend** (NOT foodis-db!)

## Step 3: Upload Files to Railway

Upload both files to Railway:

```bash
railway up railway_data.json
railway up import_to_railway.py
```

## Step 4: Run Import on Railway

```bash
railway run python import_to_railway.py
```

## Step 5: Verify Data

Check your Railway database:

```bash
railway run python manage.py shell
```

Then in the shell:
```python
from core.models import User
from client.models import Restaurant, MenuItem

print(f"Users: {User.objects.count()}")
print(f"Restaurants: {Restaurant.objects.count()}")
print(f"Menu Items: {MenuItem.objects.count()}")
```

## Alternative: Push to Git and Deploy

If Railway CLI upload doesn't work:

1. Add files to git:
```bash
git add transfer_to_railway.py import_to_railway.py
git commit -m "Add data transfer scripts"
git push
```

2. Wait for Railway to deploy

3. Run via Railway dashboard:
   - Go to Railway Dashboard → foodis-backend
   - Click "Shell" or "Terminal"
   - Run: `python transfer_to_railway.py` (locally first)
   - Upload `railway_data.json` manually
   - Run: `python import_to_railway.py`

## Quick Summary

```bash
# Local machine
python transfer_to_railway.py

# Link to backend service
railway link  # Select foodis-backend!

# Upload files
railway up railway_data.json
railway up import_to_railway.py

# Run import
railway run python import_to_railway.py
```

Done! Your Railway database now has all your local data.
