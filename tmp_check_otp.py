import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from client.models import Order
from restaurant.serializers import OrderSerializer
from rest_framework.test import APIRequestFactory
from core.models import User

# Restaurant owner is Mahesh Sharma (ID 3), or maybe another user. Let's find Biryani Boulevard owner
from client.models import Restaurant
restaurant = Restaurant.objects.filter(name__icontains="Biryani Boulevard").first()
print(f"Restaurant: {restaurant.name}, Owner: {restaurant.owner}")

orders = Order.objects.filter(restaurant=restaurant).order_by('-id')[:2]

factory = APIRequestFactory()
request = factory.get('/')
from rest_framework.request import Request
django_request = Request(request)
django_request.user = restaurant.owner

for order in orders:
    print(f"\nOrder #{order.order_id} ({order.status}):")
    # Check DB otp
    print(f"DB pickup_otp: {order.pickup_otp}")
    
    # Check Redis Cache OTP
    from client.services.otp_service import OTPService
    cached_otp = OTPService.get_valid_otp(order, 'PICKUP')
    print(f"Cached OTP: {cached_otp}")
    
    # Check what Serializer outputs
    serializer = OrderSerializer(order, context={'request': django_request})
    print(f"Serializer output pickup_otp: {serializer.data.get('pickup_otp')}")
