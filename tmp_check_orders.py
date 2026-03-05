import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from client.models import Order
from restaurant.models import Restaurant
from rider_legacy.models import RiderProfile

riders = RiderProfile.objects.filter(rider__role='RIDER')
print(f"Rider Cities: {list(riders.values_list('city', flat=True).distinct())}")

rests = Restaurant.objects.all()
print(f"Restaurant Cities: {list(rests.values_list('city', flat=True).distinct())}")

orders = Order.objects.filter(status__in=['CONFIRMED', 'PREPARING', 'READY'])
print(f"Available Orders: {orders.count()}")
if orders.exists():
    for o in orders[:5]:
        print(f"Order #{o.id} - Rest City: {o.restaurant.city} - Status: {o.status} - Rider: {o.rider}")
