# Complete Railway Setup Guide

## Step 1: Connect Backend to Database

### 1.1 Go to Railway Dashboard
- Open: https://railway.app
- Go to your project: **soothing-passion**

### 1.2 Connect Database to Backend
1. Click on **foodis-backend** service
2. Go to **Variables** tab
3. Click **+ New Variable** → **Add Reference**
4. Select: **foodis-db** → **DATABASE_URL**
5. Click **Add**

This creates a `DATABASE_URL` variable in your backend that points to your PostgreSQL database.

### 1.3 Verify Connection
1. Go to **foodis-backend** → **Deployments**
2. Wait for it to redeploy (automatic after adding variable)
3. Check logs - should see "Database connected" or similar

## Step 2: Run Migrations on Railway

After database is connected, run migrations:

### Option A: Via Railway Dashboard
1. Go to **foodis-backend** service
2. Click **Settings** → scroll to **Deploy**
3. Under "Custom Start Command", temporarily change to:
   ```
   python manage.py migrate && gunicorn foodis.wsgi:application
   ```
4. Save and wait for redeploy

### Option B: Via Railway CLI
```bash
railway link  # Select foodis-backend
railway run python manage.py migrate
```

## Step 3: Create Superuser on Railway

```bash
railway link  # Select foodis-backend
railway run python manage.py createsuperuser
```

Or use the script:
```bash
railway run python scripts/create_superuser.py
```

## Step 4: Transfer Local Data

### 4.1 Export Local Data
On your local machine:
```bash
python transfer_to_railway.py
```

This creates `railway_data.json`

### 4.2 Push to Git
```bash
git add transfer_to_railway.py import_to_railway.py railway_data.json
git commit -m "Add data transfer scripts"
git push
```

### 4.3 Wait for Railway Deploy
Railway will automatically deploy when you push to git.

### 4.4 Run Import on Railway
```bash
railway link  # Select foodis-backend
railway run python import_to_railway.py
```

## Step 5: Verify Everything Works

### Check Database Has Data
```bash
railway run python manage.py shell
```

In the shell:
```python
from core.models import User
from client.models import Restaurant, MenuItem

print(f"Users: {User.objects.count()}")
print(f"Restaurants: {Restaurant.objects.count()}")
print(f"Menu Items: {MenuItem.objects.count()}")
exit()
```

### Test API Endpoint
Get your Railway URL from dashboard (e.g., `https://foodis-backend-production.up.railway.app`)

Test:
```bash
curl https://your-railway-url.up.railway.app/health/
```

Should return: `{"status": "healthy"}`

## Quick Checklist

- [ ] Database connected to backend (DATABASE_URL variable added)
- [ ] Migrations run on Railway
- [ ] Superuser created
- [ ] Local data exported (railway_data.json)
- [ ] Scripts pushed to git
- [ ] Data imported to Railway
- [ ] API responding correctly

## Troubleshooting

### "No DATABASE_URL found"
- Go to foodis-backend → Variables
- Add reference to foodis-db → DATABASE_URL

### "Relation does not exist"
- Run migrations: `railway run python manage.py migrate`

### "No data in database"
- Make sure you ran: `railway run python import_to_railway.py`
- Check railway_data.json exists in your Railway deployment

### "Connection refused"
- Make sure backend is deployed and running
- Check deployment logs for errors

## Environment Variables Needed

Your **foodis-backend** should have these variables:

```
DATABASE_URL=postgresql://... (reference from foodis-db)
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=*
CLOUDINARY_CLOUD_NAME=your-cloudinary-name
CLOUDINARY_API_KEY=your-key
CLOUDINARY_API_SECRET=your-secret
EMAIL_HOST_PASSWORD=your-sendgrid-key
RAZORPAY_KEY_ID=your-razorpay-key
RAZORPAY_KEY_SECRET=your-razorpay-secret
GOOGLE_MAPS_API_KEY=your-google-maps-key
```

Copy these from your local `.env` file to Railway Variables.
