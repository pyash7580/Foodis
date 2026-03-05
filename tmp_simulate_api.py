import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from rest_framework.test import APIRequestFactory
from core.models import User
from rider_legacy.views import OrderViewSet

user = User.objects.get(id=8) # Default to ID 8
# Wait, let's actually check which user is Rider 508.
# In the previous logs: "Testing for user ID 508"
# Let's test with ID 508 and 8
for uid in [8, 508]:
    try:
        user = User.objects.get(id=uid)
        print(f"\n--- Testing User {uid} ({user.name}) ---")
        factory = APIRequestFactory()
        request = factory.get('/api/rider/orders/available/')
        from rest_framework.request import Request
        django_request = Request(request)
        django_request.user = user

        view = OrderViewSet()
        view.request = django_request
        view.format_kwarg = None

        response = view.available(django_request)
        print("STATUS CODE:", response.status_code)
        import json
        
        # We need to render the response to get the data if it's not rendered
        if hasattr(response, 'data'):
            print("DATA:", json.dumps(response.data, indent=2, default=str))
        else:
            print("No response.data")
    except Exception as e:
        print(f"Error for user {uid}: {e}")
