web: gunicorn foodis.wsgi:application --workers 2 --timeout 120 --bind 0.0.0.0:$PORT
worker: celery -A foodis worker --loglevel=info
beat: celery -A foodis beat --loglevel=info
