from client.views import RestaurantViewSet
from django.test import RequestFactory
import traceback
import math
from core.views import find_user_by_phone
from core.models import User

# Bug 1: Restaurant 500
try:
    print("Testing Restaurant 500 error...")
    factory = RequestFactory()
    from rest_framework.request import Request
    django_request = factory.get('/api/client/restaurants/?latitude=23.03808&longitude=72.56212')
    request = Request(django_request)
    view = RestaurantViewSet()
    view.request = request
    qs = view.get_queryset()
    print("Queryset count:", list(qs))
except Exception as e:
    print("Exception caught in Restaurant:")
    traceback.print_exc()

# Bug 2: User phone 9824948665
print("\nTesting User 9824948665...")
phone = "9824948665"
user = find_user_by_phone(phone)
if user:
    print("User found:", user.phone, user.role, user.is_active)
else:
    print("User not found via find_user_by_phone.")
    all_users = User.objects.filter(phone__contains=phone)
    if all_users.exists():
         print("But user exists with phone:", [u.phone for u in all_users])
    else:
         print("User does not exist at all in the database!")
