web: daphne -b 0.0.0.0 -p $PORT foodis.asgi:application
worker: celery -A foodis worker --loglevel=info
beat: celery -A foodis beat --loglevel=info
