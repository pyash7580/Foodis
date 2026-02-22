import os
import django
from decimal import Decimal
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from django.contrib.auth import get_user_model
from client.models import Restaurant, MenuItem, Category

User = get_user_model()

print("Step 1: Clearing existing dummy restaurants...")
Restaurant.objects.all().delete()
MenuItem.objects.all().delete()

print("Step 2: Preparing owners and categories...")
owners = []
for i in range(12):
    email = f'premiumowner{i+1}@foodis.com'
    user, _ = User.objects.get_or_create(
        email=email,
        defaults={'phone': f'+91700{i:07d}', 'name': f'Premium Owner {i+1}', 'role': 'RESTAURANT'}
    )
    user.set_password('password123')
    user.save()
    owners.append(user)

categories = ['North Indian', 'South Indian', 'Chinese', 'Desserts', 'Beverages', 'Fast Food', 'Pizzas']
cat_objects = []
for cat_name in categories:
    slug = cat_name.lower().replace(' ', '-')
    c, _ = Category.objects.get_or_create(name=cat_name, defaults={'slug': slug})
    cat_objects.append(c)


# 12 Premium Restaurants Setup mapping to their exact local files
print("Step 3: Creating 12 Premium Restaurants with Images...")

# Map of restaurant names to their corresponding premium image filenames currently sitting in media/restaurants/covers/
cover_map = {
    'Saffron Lounge': 'saffron_lounge_cover.png',
    'Thali Treasures': 'unwatermarked_Thali_Treasures.png',
    'The Coastal Spice': 'unwatermarked_The_Coastal_Spice.png',
    'The Naan Stop': 'The_Naan_Stop.png',
    'Biryani Boulevard': 'biryani_boulevard_cover.png',
    'Chaat Corner Premium': 'unwatermarked_Chaat_Corner_Premium.png',
    'Spice Symphony': 'unwatermarked_Spice_Symphony.png',
    'Tandoor Treasures': 'unwatermarked_Tandoor_Treasures.png',
    'The Curry Club': 'unwatermarked_The_Curry_Club.png',
    'Kebab Factory': 'unwatermarked_Kebab_Factory.png',
    'Wok This Way': 'unwatermarked_Wok_This_Way.png',
    'Taste of Gujarat': 'unwatermarked_The_Rajwada.png'
}

restaurants_data = [
    {'name': 'Saffron Lounge', 'cuisine': 'North Indian', 'city': 'Ahmedabad', 'lat': 23.0225, 'lng': 72.5714, 'fee': 35},
    {'name': 'Thali Treasures', 'cuisine': 'Gujarati', 'city': 'Ahmedabad', 'lat': 23.0330, 'lng': 72.5800, 'fee': 30},
    {'name': 'The Coastal Spice', 'cuisine': 'Seafood', 'city': 'Surat', 'lat': 21.1702, 'lng': 72.8311, 'fee': 50},
    {'name': 'The Naan Stop', 'cuisine': 'North Indian', 'city': 'Surat', 'lat': 21.1800, 'lng': 72.8400, 'fee': 25},
    {'name': 'Biryani Boulevard', 'cuisine': 'Biryani', 'city': 'Vadodara', 'lat': 22.3072, 'lng': 73.1812, 'fee': 40},
    {'name': 'Chaat Corner Premium', 'cuisine': 'Street Food', 'city': 'Vadodara', 'lat': 22.3150, 'lng': 73.1900, 'fee': 20},
    {'name': 'Spice Symphony', 'cuisine': 'South Indian', 'city': 'Rajkot', 'lat': 22.3039, 'lng': 70.8022, 'fee': 35},
    {'name': 'Tandoor Treasures', 'cuisine': 'Tandoori', 'city': 'Rajkot', 'lat': 22.3100, 'lng': 70.8100, 'fee': 45},
    {'name': 'The Curry Club', 'cuisine': 'Multi-Cuisine', 'city': 'Gandhinagar', 'lat': 23.2156, 'lng': 72.6369, 'fee': 30},
    {'name': 'Kebab Factory', 'cuisine': 'Mughlai', 'city': 'Gandhinagar', 'lat': 23.2250, 'lng': 72.6450, 'fee': 55},
    {'name': 'Wok This Way', 'cuisine': 'Chinese', 'city': 'Mehsana', 'lat': 23.5880, 'lng': 72.3693, 'fee': 25},
    {'name': 'Taste of Gujarat', 'cuisine': 'Gujarati', 'city': 'Himmatnagar', 'lat': 23.5979, 'lng': 72.9698, 'fee': 30},
]

# Dish name to media image file mapping (to be added locally)
dish_images = {
    'Paneer Tikka': 'paneer_tikka.png',
    'Butter Chicken': 'butter_chicken_premium.jpg',
    'Dal Makhani': 'dal_makhani_premium.jpg',
    'Garlic Naan': 'garlic_naan_premium.jpg',
    'Chicken Biryani': 'chicken_biryani_premium.jpg',
    'Veg Biryani': 'veg_biryani_premium.jpg',
    'Masala Dosa': 'masala_dosa_premium.jpg',
    'Idli Sambar': 'idli_sambar_premium.jpg',
    'Chilli Chicken': 'chilli_chicken_premium.jpg',
    'Hakka Noodles': 'hakka_noodles_premium.jpg',
    'Gulab Jamun': 'gulab_jamun.png',
    'Samosa': 'samosa.png'
}

created_restaurants = []

from django.db import transaction

# Using transaction to make it faster
with transaction.atomic():
    for i, data in enumerate(restaurants_data):
        slug = data['name'].lower().replace(' ', '-')
        r, created = Restaurant.objects.get_or_create(
            slug=slug,
            defaults={
                'name': data['name'],
                'owner': owners[i],
                'description': f"Premium {data['cuisine']} restaurant offering authentic flavors.",
                'city': data['city'],
                'address': f"Central {data['city']}, Gujarat",
                'state': 'Gujarat',
                'pincode': '380001',
                'latitude': data['lat'],
                'longitude': data['lng'],
                'phone': f'+91980000{i:04d}',
                'delivery_fee': Decimal(str(data['fee'])),
                'delivery_time': random.randint(25, 45),
                'rating': round(random.uniform(4.2, 4.9), 1),
                'is_active': True,
                'status': 'APPROVED',
                'cuisine': data['cuisine']
            }
        )
        # Assign image dynamically based on cover_map
        cover_file = cover_map.get(data['name'])
        if cover_file:
            r.cover_image.name = f"restaurants/covers/{cover_file}"
            r.save()
            
        print(f"Created: {r.name} with image {cover_file}")
        
        # Add 4 random premium dishes to each restaurant
        selected_dishes = random.sample(list(dish_images.keys()), 4)
        for d_name in selected_dishes:
            price = random.randint(150, 450)
            veg_type = 'VEG' if 'Chicken' not in d_name and 'Mutton' not in d_name else 'NON_VEG'
            item, _ = MenuItem.objects.get_or_create(
                restaurant=r,
                name=d_name,
                defaults={
                    'description': f"Delicious {d_name}",
                    'price': Decimal(str(price)),
                    'veg_type': veg_type,
                    'is_available': True,
                    'preparation_time': random.randint(15, 30)
                }
            )
            # Assign item image
            item_file = dish_images.get(d_name)
            if item_file:
                item.image.name = f"menu_items/{item_file}"
                item.save()

print("\nDone! All realistic restaurants and premium images have been seeded into the Neon Database successfully.")
