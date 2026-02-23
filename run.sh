#!/bin/bash
# Apply migrations (optional but recommended on deploy)
python manage.py migrate --noinput

# Start the application using Gunicorn with Uvicorn workers for ASGI/WebSockets
gunicorn foodis.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
