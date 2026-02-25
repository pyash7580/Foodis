#!/bin/bash

echo "🚀 Starting Foodis Production Server..."

echo "🌍 PORT = $PORT"

# Ensure staticfiles directory exists
mkdir -p staticfiles

# Run migrations
echo "⚙️ Running migrations..."
python manage.py migrate --noinput
echo "✅ Migrations done"

# Collect static files
echo "⚙️ Collecting static files..."
python manage.py collectstatic --noinput --clear
echo "✅ Static files collected"

# Debug: List staticfiles to confirm growth
echo "📁 Listing staticfiles content:"
ls -R staticfiles | head -n 20

# Start Gunicorn
echo "🚀 Starting Gunicorn..."
gunicorn foodis.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120