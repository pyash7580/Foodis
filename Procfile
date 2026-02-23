web: python manage.py migrate --noinput && gunicorn foodis.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
worker: celery -A foodis worker --loglevel=info
beat: celery -A foodis beat --loglevel=info
