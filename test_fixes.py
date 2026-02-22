import os
import sys

# Setup Django Environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodis.settings")
import django
django.setup()

from django.conf import settings
settings.ALLOWED_HOSTS.append('testserver')

from core.models import User
from client.models import Restaurant
from core.views import send_otp_view
from client.views import RestaurantViewSet
from rest_framework.test import APIRequestFactory

factory = APIRequestFactory()

print("--- TESTING OTP FLOW ---")
# Pick an existing user phone
existing_user = User.objects.filter(role='CLIENT').first()
if existing_user:
    phone = existing_user.phone
    print(f"Testing existing user: {phone}")
    request = factory.post('/api/auth/send-otp/', {'phone': phone}, format='json', HTTP_HOST='localhost')
    response = send_otp_view(request)
    if hasattr(response, 'data'):
        print(f"Response for existing user: flow={response.data.get('flow')}, is_new={response.data.get('is_new_user')}")
else:
    print("No existing client users found")

print("Testing new user: 9999999999")
request = factory.post('/api/auth/send-otp/', {'phone': '9999999999'}, format='json', HTTP_HOST='localhost')
response = send_otp_view(request)
if hasattr(response, 'data'):
    print(f"Response for new user: flow={response.data.get('flow')}, is_new={response.data.get('is_new_user')}")

print("\n--- TESTING RESTAURANT LISTING ---")
owner, _ = User.objects.get_or_create(phone="8888888888", defaults={"name": "Test Owner", "role": "RESTAURANT"})
test_rest, created = Restaurant.objects.get_or_create(
    owner=owner, 
    slug="test-rest",
    defaults={
        "name": "Test Rest Bad Coords", 
        "address": "test", 
        "city": "test", 
        "state": "test", 
        "pincode": "123",
        "status": "APPROVED",
        "latitude": None,
        "longitude": None
    }
)
if not created and test_rest.latitude is not None:
    test_rest.latitude = None
    test_rest.longitude = None
    test_rest.save()

request = factory.get('/api/client/restaurants/?latitude=23.0&longitude=72.0&radius=50000', format='json', HTTP_HOST='localhost')
view = RestaurantViewSet.as_view({'get': 'list'})
try:
    response = view(request)
    if hasattr(response, 'data') and 'results' in response.data:
        count = len(response.data['results'])
    elif hasattr(response, 'data'):
        count = len(response.data)
    else:
        count = 0
    print(f"Success! Retrieved {count} restaurants without crashing.")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"FAILED: {e}")

if created:
    test_rest.delete()
    owner.delete()
