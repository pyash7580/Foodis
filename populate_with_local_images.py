"""
Populate database with local restaurant images from Downloads folder.
Copies images to media folder and creates restaurants with them.
"""
import os
import django
import shutil
from pathlib import Path
from decimal import Decimal
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from django.contrib.auth import get_user_model
from client.models import Restaurant, MenuItem, Category
from django.db import transaction

User = get_user_model()

print("=" * 80)
print("POPULATING DATABASE WITH LOCAL RESTAURANT IMAGES")
print("=" * 80)

# Path to your images
IMAGES_SOURCE = Path(r"C:\Users\ASUS\Downloads\resturent")
IMAGES_DEST = Path("media/restaurants/covers")

# Create destination folder if not exists
IMAGES_DEST.mkdir(parents=True, exist_ok=True)

# Step 1: Copy images from Downloads to media folder
print("\nStep 1: Copying images from Downloads to media folder...")
image_mapping = {}  # Maps restaurant name to image filename

if IMAGES_SOURCE.exists():
    for image_file in sorted(IMAGES_SOURCE.glob("*.png")):
        dest_path = IMAGES_DEST / image_file.name
        try:
            shutil.copy2(image_file, dest_path)
            rest_name = image_file.stem  # Filename without extension
            image_mapping[rest_name] = image_file.name
            print(f"  [OK] Copied: {image_file.name} -> media/restaurants/covers/")
        except Exception as e:
            print(f"  [ERROR] Failed to copy {image_file.name}: {e}")
else:
    print(f"  [ERROR] Image source folder not found: {IMAGES_SOURCE}")

print(f"\n  Total images copied: {len(image_mapping)}")

# Step 2: Create owners (one unique owner per restaurant)
print("\nStep 2: Creating restaurant owners...")
import time
owners = []
timestamp = int(time.time() * 1000000) % 1000000
for i in range(len(image_mapping)):
    email = f'owner{i+1}_{timestamp}@foodis.local'
    phone = f'+919899{timestamp + i:05d}'  # Unique phone for each owner
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'phone': phone,
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
categories_list = ['North Indian', 'South Indian', 'Chinese', 'Desserts', 'Pizza', 'Biryani', 'Fast Food', 'Mughlai', 'Street Food', 'Seafood']
categories = []
for cat_name in categories_list:
    c, created = Category.objects.get_or_create(
        name=cat_name,
        defaults={'slug': cat_name.lower().replace(' ', '-'), 'is_active': True}
    )
    categories.append(c)
    if created:
        print(f"  [OK] Created category: {cat_name}")

# Step 4: Create restaurants with local images
print(f"\nStep 4: Creating {len(image_mapping)} restaurants with local images...")

# Map restaurant names to details
restaurant_details = {
    'Thali Treasures': {'cuisine': 'Gujarati', 'city': 'Himmatnagar', 'lat': 23.5979, 'lng': 72.9698, 'fee': 30},
    'The Naan Stop': {'cuisine': 'North Indian', 'city': 'Mehsana', 'lat': 23.5880, 'lng': 72.3693, 'fee': 25},
    'The Coastal Spice': {'cuisine': 'Seafood', 'city': 'Himmatnagar', 'lat': 23.5950, 'lng': 72.9700, 'fee': 50},
    'Tandoor Treasures': {'cuisine': 'Tandoori', 'city': 'Mehsana', 'lat': 23.5900, 'lng': 72.3700, 'fee': 45},
    'The Curry Club': {'cuisine': 'Multi-Cuisine', 'city': 'Himmatnagar', 'lat': 23.5990, 'lng': 72.9695, 'fee': 30},
    'Kebab Factory': {'cuisine': 'Mughlai', 'city': 'Mehsana', 'lat': 23.5875, 'lng': 72.3705, 'fee': 55},
    'Wok This Way': {'cuisine': 'Chinese', 'city': 'Himmatnagar', 'lat': 23.5980, 'lng': 72.9696, 'fee': 25},
    'The Rajwada': {'cuisine': 'North Indian', 'city': 'Mehsana', 'lat': 23.5870, 'lng': 72.3690, 'fee': 40},
    'Spice Symphony': {'cuisine': 'South Indian', 'city': 'Himmatnagar', 'lat': 23.5985, 'lng': 72.9700, 'fee': 35},
    'Chaat Corner Premium': {'cuisine': 'Street Food', 'city': 'Mehsana', 'lat': 23.5895, 'lng': 72.3710, 'fee': 20},
    'popes cafe': {'cuisine': 'Fast Food', 'city': 'Himmatnagar', 'lat': 23.5975, 'lng': 72.9690, 'fee': 22},
    'Naan Basket': {'cuisine': 'North Indian', 'city': 'Mehsana', 'lat': 23.5885, 'lng': 72.3695, 'fee': 28},
    'The Dhaba Deluxe': {'cuisine': 'Mughlai', 'city': 'Himmatnagar', 'lat': 23.5982, 'lng': 72.9698, 'fee': 38},
    'The Vintage Kitchen': {'cuisine': 'Multi-Cuisine', 'city': 'Mehsana', 'lat': 23.5880, 'lng': 72.3692, 'fee': 32},
    'The Spice Route': {'cuisine': 'Gujarati', 'city': 'Himmatnagar', 'lat': 23.5980, 'lng': 72.9699, 'fee': 35},
    'Taj Palace': {'cuisine': 'North Indian', 'city': 'Mehsana', 'lat': 23.5887, 'lng': 72.3700, 'fee': 48},
}

sample_dishes = [
    'Paneer Tikka', 'Butter Chicken', 'Dal Makhani', 'Garlic Naan',
    'Chicken Biryani', 'Veg Biryani', 'Masala Dosa', 'Idli Sambar',
    'Chilli Chicken', 'Hakka Noodles', 'Gulab Jamun', 'Samosa',
    'Pizza Margherita', 'Tandoori Chicken', 'Fried Rice', 'Momo'
]

with transaction.atomic():
    for i, (rest_name, image_filename) in enumerate(sorted(image_mapping.items())):
        slug = rest_name.lower().replace(' ', '-').replace('(', '').replace(')', '')

        # Get details or use defaults
        details = restaurant_details.get(rest_name, {})
        cuisine = details.get('cuisine', 'North Indian')
        city = details.get('city', 'Mehsana')
        lat = details.get('lat', 23.5880)
        lng = details.get('lng', 72.3693)
        fee = details.get('fee', 30)

        r, created = Restaurant.objects.get_or_create(
            slug=slug,
            defaults={
                'name': rest_name,
                'owner': owners[i],
                'description': f"Delicious {cuisine} restaurant offering authentic flavors",
                'city': city,
                'address': f"Central {city}, Gujarat",
                'state': 'Gujarat',
                'pincode': '380001',
                'latitude': Decimal(str(lat)),
                'longitude': Decimal(str(lng)),
                'phone': f'+9198000{i:05d}',
                'delivery_fee': Decimal(str(fee)),
                'delivery_time': random.randint(25, 45),
                'rating': Decimal(str(round(random.uniform(4.0, 4.9), 1))),
                'total_ratings': random.randint(50, 500),
                'is_active': True,
                'status': 'APPROVED',
                'cuisine': cuisine
            }
        )

        # Set image to local file path (relative to MEDIA_ROOT)
        if created or not r.cover_image:
            r.cover_image.name = f"restaurants/covers/{image_filename}"
            r.save()

        print(f"  [OK] Created: {rest_name} ({cuisine}) - City: {city}")

        # Add 3-4 random dishes
        selected_dishes = random.sample(sample_dishes, random.randint(3, 4))
        for dish_name in selected_dishes:
            price = Decimal(str(random.randint(150, 450)))
            veg = 'VEG' if random.choice([True, False]) else 'NON_VEG'

            item, _ = MenuItem.objects.get_or_create(
                restaurant=r,
                name=dish_name,
                defaults={
                    'description': f"Delicious homemade {dish_name}",
                    'price': price,
                    'veg_type': veg,
                    'is_available': True,
                    'preparation_time': random.randint(15, 35),
                    'rating': Decimal(str(round(random.uniform(4.0, 4.8), 1)))
                }
            )

print("\n" + "=" * 80)
print("[OK] SUCCESS! Database populated with local restaurant images")
print("=" * 80)
print("\nDetails:")
print(f"  - Restaurants created: {len(image_mapping)}")
print(f"  - Images copied to: media/restaurants/covers/")
print(f"  - Cities: Mehsana, Himmatnagar")
print(f"  - Menu items: ~{len(image_mapping) * 3} dishes across all restaurants")
print(f"\nNow test on your site:")
print(f"  1. Visit: http://localhost:3000/client")
print(f"  2. All restaurant cards should show images")
print(f"  3. Images are from your local files (not Pexels)")
print(f"  4. No 404 errors")
print("\n" + "=" * 80)
