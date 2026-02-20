import os
import django
import random
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from client.models import Order, User, Restaurant

def populate_v2():
    print("Injecting City Trends...")
    cities = ['Mumbai', 'Bangalore', 'Delhi', 'Chennai', 'Hyderabad']
    for i, city in enumerate(cities):
        owner_email = f"owner_{city.lower()}@foodis.com"
        try:
            user = User.objects.get(email=owner_email)
            restaurant = user.restaurant
        except User.DoesNotExist:
            user = User.objects.create_user(
                phone=f'+9198{i}0000000',
                email=owner_email,
                name=f'{city} Bistro',
                role='RESTAURANT',
                password='password'
            )
            restaurant = Restaurant.objects.create(
                owner=user,
                name=f'{city} Spice Hub',
                slug=f'{city.lower()}-spice-hub',
                phone=f'98{i}0000000',
                address='123 Main St',
                city=city,
                state='State',
                pincode='100001',
                latitude=Decimal('12.0'),
                longitude=Decimal('77.0'),
                status='APPROVED',
                image='restaurants/default.jpg' 
            )
        
        client_user = User.objects.filter(role='CLIENT').first()
        if not client_user:
            client_user = User.objects.create_user(phone='+919999999999', name='Test Client', role='CLIENT')

        for _ in range(5):
            Order.objects.create(
                user=client_user,
                restaurant=restaurant,
                total=Decimal('500.00'),
                subtotal=Decimal('500.00'),
                status='DELIVERED',
                payment_status='PAID',
                payment_method='RAZORPAY',
                placed_at=timezone.now() - timedelta(days=random.randint(1, 25)),
                delivery_latitude=Decimal('0'), delivery_longitude=Decimal('0'), delivery_phone='000'
            )
    print("City Trends Done.")

if __name__ == '__main__':
    populate_v2()
