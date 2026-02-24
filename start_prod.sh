#!/bin/bash

echo "🚀 Starting Foodis Production Server..."

python manage.py migrate --noinput

echo "✅ Migrations done"

gunicorn foodis.wsgi:application --bind 0.0.0.0:$PORT
