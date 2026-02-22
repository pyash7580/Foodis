web: gunicorn foodis.wsgi:application --bind 0.0.0.0:$PORT
worker: celery -A foodis worker --loglevel=info
beat: celery -A foodis beat --loglevel=info
