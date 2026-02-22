"""
Populate production database with restaurants WITH WORKING IMAGES.
Uses external Pexels URLs so images display on production (Render).
This solves the image display issue by using image URLs instead of local files.
"""
import os
import django
from decimal import Decimal
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from django.contrib.auth import get_user_model
from client.models import Restaurant, MenuItem, Category
from django.db import transaction

User = get_user_model()

print("=" * 80)
print("PRODUCTION IMAGE SEEDING - Using External Pexels URLs")
print("=" * 80)

# Step 1: Clear existing data
print("\nStep 1: Clearing existing restaurants...")
Restaurant.objects.all().delete()

# Step 2: Create owners
print("Step 2: Creating restaurant owners...")
owners = []
for i in range(10):
    email = f'owner{i+1}@foodis.local'
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'phone': f'+9198000{i:05d}',
            'name': f'Owner {i+1}',
            'role': 'RESTAURANT'
        }
    )
    user.set_password('password123')
    user.save()
    owners.append(user)
    if created:
        print(f"  [OK] Created owner: {user.name}")

# Step 3: Create categories
print("\nStep 3: Creating food categories...")
categories_list = ['North Indian', 'South Indian', 'Chinese', 'Desserts', 'Pizza', 'Biryani', 'Fast Food']
categories = []
for cat_name in categories_list:
    c, created = Category.objects.get_or_create(
        name=cat_name,
        defaults={'slug': cat_name.lower().replace(' ', '-'), 'is_active': True}
    )
    categories.append(c)
    if created:
        print(f"  [OK] Created category: {cat_name}")

# Step 4: Restaurant data with EXTERNAL image URLs (Pexels - free & public)
print("\nStep 4: Creating 10 restaurants with external images...")

restaurants_data = [
    {
        'name': 'Saffron Lounge',
        'cuisine': 'North Indian',
        'city': 'Mehsana',
        'lat': 23.5880,
        'lng': 72.3693,
        'fee': 35,
        'image_url': 'https://images.pexels.com/photos/1410235/pexels-photo-1410235.jpeg?auto=compress&cs=tinysrgb&w=400',  # Indian food
        'description': 'Authentic North Indian cuisine with rich flavors and traditional recipes'
    },
    {
        'name': 'Thali Treasures',
        'cuisine': 'Gujarati',
        'city': 'Himmatnagar',
        'lat': 23.5979,
        'lng': 72.9698,
        'fee': 30,
        'image_url': 'https://images.pexels.com/photos/1092730/pexels-photo-1092730.jpeg?auto=compress&cs=tinysrgb&w=400',  # Food plate
        'description': 'Traditional Gujarati thali with authentic local recipes and fresh ingredients'
    },
    {
        'name': 'Pizza Paradise',
        'cuisine': 'Pizza',
        'city': 'Mehsana',
        'lat': 23.5900,
        'lng': 72.3700,
        'fee': 40,
        'image_url': 'https://images.pexels.com/photos/825661/pexels-photo-825661.jpeg?auto=compress&cs=tinysrgb&w=400',  # Pizza
        'description': 'Delicious wood-fired pizzas with premium toppings and fresh mozzarella'
    },
    {
        'name': 'Biryani Boulevard',
        'cuisine': 'Biryani',
        'city': 'Himmatnagar',
        'lat': 23.5950,
        'lng': 72.9700,
        'fee': 45,
        'image_url': 'https://images.pexels.com/photos/1092747/pexels-photo-1092747.jpeg?auto=compress&cs=tinysrgb&w=400',  # Rice dish
        'description': 'Aromatic biryani cooked with fragrant rice, meat, and authentic spices'
    },
    {
        'name': 'The Curry Club',
        'cuisine': 'North Indian',
        'city': 'Mehsana',
        'lat': 23.5880,
        'lng': 72.3695,
        'fee': 35,
        'image_url': 'https://images.pexels.com/photos/1638261/pexels-photo-1638261.jpeg?auto=compress&cs=tinysrgb&w=400',  # Spicy food
        'description': 'Multi-cuisine restaurant featuring traditional Indian curries and gravies'
    },
    {
        'name': 'South Indian Deli',
        'cuisine': 'South Indian',
        'city': 'Himmatnagar',
        'lat': 23.5990,
        'lng': 72.9695,
        'fee': 28,
        'image_url': 'https://images.pexels.com/photos/406152/pexels-photo-406152.jpeg?auto=compress&cs=tinysrgb&w=400',  # Food closeup
        'description': 'Authentic South Indian cuisine - dosa, idli, sambar with traditional recipes'
    },
    {
        'name': 'Wok Express',
        'cuisine': 'Chinese',
        'city': 'Mehsana',
        'lat': 23.5870,
        'lng': 72.3700,
        'fee': 32,
        'image_url': 'https://images.pexels.com/photos/1624487/pexels-photo-1624487.jpeg?auto=compress&cs=tinysrgb&w=400',  # Asian noodles
        'description': 'Chinese cooking with fresh vegetables, noodles, and authentic recipes'
    },
    {
        'name': 'Sweet Cravings',
        'cuisine': 'Desserts',
        'city': 'Himmatnagar',
        'lat': 23.6000,
        'lng': 72.9700,
        'fee': 25,
        'image_url': 'https://images.pexels.com/photos/905847/pexels-photo-905847.jpeg?auto=compress&cs=tinysrgb&w=400',  # Desserts
        'description': 'Premium desserts and sweets - cakes, pastries, and traditional Indian mithai'
    },
    {
        'name': 'Fast Food Junction',
        'cuisine': 'Fast Food',
        'city': 'Mehsana',
        'lat': 23.5875,
        'lng': 72.3705,
        'fee': 20,
        'image_url': 'https://images.pexels.com/photos/1092360/pexels-photo-1092360.jpeg?auto=compress&cs=tinysrgb&w=400',  # Burger
        'description': 'Quick service fast food with burgers, fries, and sandwiches'
    },
    {
        'name': 'Royal Taste',
        'cuisine': 'North Indian',
        'city': 'Himmatnagar',
        'lat': 23.5980,
        'lng': 72.9696,
        'fee': 50,
        'image_url': 'https://images.pexels.com/photos/1995558/pexels-photo-1995558.jpeg?auto=compress&cs=tinysrgb&w=400',  # Fine dining
        'description': 'Premium North Indian cuisine with exotic spices and royal presentation'
    },
]

# Sample dish names
dish_names = [
    'Paneer Tikka', 'Butter Chicken', 'Dal Makhani', 'Garlic Naan',
    'Chicken Biryani', 'Veg Biryani', 'Masala Dosa', 'Idli Sambar',
    'Chilli Chicken', 'Hakka Noodles', 'Gulab Jamun', 'Samosa',
    'Pizza Margherita', 'Tandoori Chicken', 'Fried Rice', 'Momo'
]

#  Create restaurants with image URLs
with transaction.atomic():
    for i, data in enumerate(restaurants_data):
        slug = data['name'].lower().replace(' ', '-')
        r, created = Restaurant.objects.get_or_create(
            slug=slug,
            defaults={
                'name': data['name'],
                'owner': owners[i % len(owners)],
                'description': data['description'],
                'city': data['city'],
                'address': f"Central {data['city']}, Gujarat",
                'state': 'Gujarat',
                'pincode': '380001',
                'latitude': Decimal(str(data['lat'])),
                'longitude': Decimal(str(data['lng'])),
                'phone': f'+9198000{i:05d}',
                'delivery_fee': Decimal(str(data['fee'])),
                'delivery_time': random.randint(25, 45),
                'rating': Decimal(str(round(random.uniform(4.0, 4.9), 1))),
                'total_ratings': random.randint(50, 500),
                'is_active': True,
                'status': 'APPROVED',
                'cuisine': data['cuisine'],
                'image_url': data['image_url']  # Store external URL directly
            }
        )

        # If restaurant existed but didn't have image_url, update it
        if not created and not r.image_url:
            r.image_url = data['image_url']
            r.save()

        print(f"  [OK] Created: {r.name} ({data['cuisine']}) - Mehsana/Himmatnagar")

        # Add 3-4 random dishes to each restaurant
        selected_dishes = random.sample(dish_names, random.randint(3, 4))
        for d_name in selected_dishes:
            price = Decimal(str(random.randint(150, 450)))
            veg = 'VEG' if random.choice([True, False]) else 'NON_VEG'

            item, _ = MenuItem.objects.get_or_create(
                restaurant=r,
                name=d_name,
                defaults={
                    'description': f"Delicious homemade {d_name}",
                    'price': price,
                    'veg_type': veg,
                    'is_available': True,
                    'preparation_time': random.randint(15, 35),
                    'rating': Decimal(str(round(random.uniform(4.0, 4.8), 1)))
                }
            )

print("\n" + "=" * 80)
print("[OK] SUCCESS! Database populated with 10 restaurants + images")
print("=" * 80)
print("\nDetails:")
print(f"  • Restaurants created: 10")
print(f"  • Cities: Mehsana, Himmatnagar")
print(f"  • Image URLs: External Pexels URLs (work on production)")
print(f"  • Menu items: ~35 dishes across all restaurants")
print(f"\nNow test on your production server:")
print(f"  1. Visit: http://localhost:3000/client")
print(f"  2. Check DevTools Network tab for images")
print(f"  3. All restaurant cards should show images from Pexels")
print(f"  4. No 404 errors on image URLs")
print("\n" + "=" * 80)
