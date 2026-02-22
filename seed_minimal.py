import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from django.contrib.auth import get_user_model
from client.models import Restaurant, MenuItem

User = get_user_model()

print("Seeding minimal test data into the Remote Neon DB...")

owner1, _ = User.objects.get_or_create(
    email='testowner1@foodis.com',
    defaults={'phone': '+919999999991', 'name': 'Owner 1', 'role': 'RESTAURANT'}
)
owner1.set_password('password123'); owner1.save()

owner2, _ = User.objects.get_or_create(
    email='testowner2@foodis.com',
    defaults={'phone': '+919999999992', 'name': 'Owner 2', 'role': 'RESTAURANT'}
)
owner2.set_password('password123'); owner2.save()

owner3, _ = User.objects.get_or_create(
    email='testowner3@foodis.com',
    defaults={'phone': '+919999999993', 'name': 'Owner 3', 'role': 'RESTAURANT'}
)
owner3.set_password('password123'); owner3.save()

data = [
    {'name': 'Test Pizza HQ', 'slug': 'test-pizza-hq', 'cuisine': 'Pizza', 'city': 'Ahmedabad', 'lat': 23.0225, 'lng': 72.5714, 'owner': owner1},
    {'name': 'Burger Town', 'slug': 'burger-town-x', 'cuisine': 'Burger', 'city': 'Mehsana', 'lat': 23.5880, 'lng': 72.3693, 'owner': owner2},
    {'name': 'Healthy Salads', 'slug': 'healthy-salads-x', 'cuisine': 'Healthy', 'city': 'Himmatnagar', 'lat': 23.5979, 'lng': 72.9698, 'owner': owner3},
]

for d in data:
    r, created = Restaurant.objects.get_or_create(
        slug=d['slug'],
        defaults={
            'name': d['name'],
            'owner': d['owner'],
            'description': f"Delicious {d['cuisine']}",
            'city': d['city'],
            'address': f"Central {d['city']}, Gujarat",
            'state': 'Gujarat',
            'pincode': '380001',
            'latitude': d['lat'],
            'longitude': d['lng'],
            'phone': '+918888888888',
            'delivery_fee': Decimal('30.00'),
            'delivery_time': 30,
            'rating': 4.5,
            'is_active': True,
            'status': 'APPROVED',
            'cuisine': d['cuisine']
        }
    )
    if created:
        print(f"Created Restaurant: {r.name}")
        
    MenuItem.objects.get_or_create(
        restaurant=r,
        name=f"Special {d['cuisine']}",
        defaults={
            'description': 'Best in town',
            'price': Decimal('150.00'),
            'veg_type': 'VEG',
            'is_available': True,
            'preparation_time': 20
        }
    )

print("Done minimal seeding.")
