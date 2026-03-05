import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from client.models import Order
from client.services.otp_service import OTPService

active_orders = Order.objects.filter(status__in=['CONFIRMED', 'PREPARING', 'READY', 'ASSIGNED', 'WAITING_FOR_RIDER'])

for order in active_orders:
    # Get existing DB OTP or generate a new one via the updated OTPService
    if not order.pickup_otp:
        print(f"Generating new permanent pickup OTP for Order {order.order_id}")
        OTPService.generate_otp(order, 'PICKUP')
    else:
        print(f"Order {order.order_id} already has persistent OTP: {order.pickup_otp}")

print(f"Fixed {active_orders.count()} active orders.")
