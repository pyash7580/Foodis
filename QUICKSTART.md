# Quick Start Guide - Foodis

## Prerequisites
- Python 3.9+
- Node.js 16+ (for frontend)
- PostgreSQL (optional - can use SQLite for development)
- Redis (for caching and OTP)

## Step 1: Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Note:** If you encounter issues with `psycopg2-binary`, you can:
1. Install PostgreSQL and add it to PATH, OR
2. Use SQLite for development by modifying `foodis/settings.py` to use SQLite instead of PostgreSQL

## Step 2: Database Setup

### Option A: Using SQLite (Easier for Development)

Modify `foodis/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### Option B: Using PostgreSQL

1. Install PostgreSQL
2. Create database:
```sql
CREATE DATABASE foodis_db;
```

3. Update `.env` file with database credentials

## Step 3: Environment Configuration

Create `.env` file in project root:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=foodis_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret
```

## Step 4: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## Step 5: Create Superuser

```bash
python manage.py createsuperuser
```

## Step 6: Start Redis

**Windows:**
- Download Redis from https://github.com/microsoftarchive/redis/releases
- Run `redis-server.exe`

**Linux/Mac:**
```bash
redis-server
```

## Step 7: Start Celery Worker (Optional - for background tasks)

Open a new terminal:

**Windows:**
```bash
start_celery.bat
```

**Linux/Mac:**
```bash
chmod +x start_celery.sh
./start_celery.sh
```

## Step 8: Start Celery Beat (Optional - for scheduled tasks)

Open another terminal:

**Windows:**
```bash
start_celery_beat.bat
```

**Linux/Mac:**
```bash
chmod +x start_celery_beat.sh
./start_celery_beat.sh
```

## Step 9: Start Django Server

**Windows:**
```bash
run_server.bat
```

**Linux/Mac:**
```bash
chmod +x run_server.sh
./run_server.sh
```

Or manually:
```bash
python manage.py runserver
```

Server will run on `http://localhost:8000`

## Step 10: Start React Frontend

Open a new terminal:

```bash
cd frontend
npm install
npm start
```

Frontend will run on `http://localhost:3000`

## Access Points

- **Client App:** http://localhost:3000/client
- **Restaurant Dashboard:** http://localhost:3000/restaurant
- **Rider Dashboard:** http://localhost:3000/rider
- **Admin Dashboard:** http://localhost:3000/admin
- **Django Admin:** http://localhost:8000/admin
- **API Root:** http://localhost:8000/api/

## Troubleshooting

### Issue: ModuleNotFoundError
**Solution:** Make sure virtual environment is activated and all dependencies are installed

### Issue: Database connection error
**Solution:** 
- Check PostgreSQL is running (if using PostgreSQL)
- Verify database credentials in `.env`
- Or switch to SQLite for development

### Issue: Redis connection error
**Solution:** 
- Make sure Redis is running
- Check `REDIS_URL` in `.env`

### Issue: Port already in use
**Solution:** 
- Change port: `python manage.py runserver 8001`
- Or kill the process using the port

## Development Notes

- For development, you can use SQLite instead of PostgreSQL
- OTP codes are printed to console in development mode
- Razorpay test mode keys can be obtained from Razorpay dashboard
- Google Maps API key is required for location features

## Next Steps

1. Create sample data using Django admin or shell
2. Test OTP login (check console for OTP code)
3. Create restaurants, menu items, and test ordering flow
4. Set up Google Maps API for location features
5. Configure Razorpay for payment testing

