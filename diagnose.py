import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from django.test import RequestFactory
from rest_framework.test import APIRequestFactory
from core.views import profile_view
from client.views import RestaurantViewSet
from core.models import User

# Create a mock user
user, _ = User.objects.get_or_create(phone='1234567890', defaults={'name': 'Test User'})

factory = APIRequestFactory()

print("--- TESTING PROFILE VIEW ---")
try:
    request = factory.get('/api/auth/profile/', SERVER_NAME='localhost')
    from rest_framework.request import Request
    # Mocking standard DRF request wrapper to include user
    from django.contrib.auth.models import AnonymousUser
    request.user = user
    # DRF wrap
    wrapped_request = Request(request)
    wrapped_request.user = user
    response = profile_view(wrapped_request)
    print("Response Status:", response.status_code)
    if response.status_code == 500:
        print("PROFILE 500 Response Data:", response.data)
except Exception as e:
    import traceback
    print("CRASH IN PROFILE SCRIPT:", traceback.format_exc())

print("\n--- TESTING RESTAURANT LIST VIEW ---")
try:
    request = factory.get('/api/client/restaurants/', SERVER_NAME='localhost')
    view = RestaurantViewSet.as_view({'get': 'list'})
    response = view(request)
    print("Response Status:", response.status_code)
except Exception as e:
    import traceback
    print("CRASH IN RESTAURANT SCRIPT:", traceback.format_exc())
