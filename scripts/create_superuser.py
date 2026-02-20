import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','foodis.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if User.objects.filter(username='admin').exists():
    print('Superuser already exists')
else:
    User.objects.create_superuser('admin','admin@example.com','adminpass')
    print('Superuser created: admin / adminpass')
