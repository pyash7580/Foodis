#!/bin/bash

echo "🚀 Starting Foodis Production Server..."

echo "🌍 PORT = $PORT"

# Ensure staticfiles directory exists for WhiteNoise
mkdir -p staticfiles

# Run migrations
python manage.py migrate --noinput

echo "✅ Migrations done"

# Collect static files
python manage.py collectstatic --noinput

echo "✅ Static files collected"

# Start Gunicorn
gunicorn foodis.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120