import os
import sys

# Setup Django Environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodis.settings")
import django
django.setup()

from django.conf import settings
settings.ALLOWED_HOSTS.append('testserver')

from core.views import send_otp_view
from rest_framework.test import APIRequestFactory

factory = APIRequestFactory()

request = factory.post('/api/auth/send-otp/', {'phone': '0000000000'}, format='json', HTTP_HOST='localhost')
response = send_otp_view(request)
if hasattr(response, 'data'):
    print(f"Response for new user: flow={response.data.get('flow')}, is_new={response.data.get('is_new_user')}")
