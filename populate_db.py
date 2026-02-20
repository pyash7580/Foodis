import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from django.contrib.auth import get_user_model
from client.models import Restaurant, MenuItem
from decimal import Decimal
import random

User = get_user_model()

print("Starting to seed database...")

# Create restaurant owner users
owners = []
for i in range(100):
    email = f'restaurant{i+1}@foodis.com'
    try:
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'phone': f'+91{9000000000 + i}',
                'name': f'Restaurant Owner {i+1}',
                'role': 'RESTAURANT'
            }
        )
        if created:
            user.set_password('password123')
            user.save()
        owners.append(user)
    except Exception as e:
        print(f"Skipping owner {email} due to error: {e}")
        # Try to fetch existing user if creation failed
        try:
            user = User.objects.get(email=email)
            owners.append(user)
        except:
            if owners:
                 owners.append(owners[-1]) # Fallback to last successful owner
            else:
                 pass

print(f"Created {len(owners)} restaurant owners")

# Premium Indian restaurant data (Gujarat Special Edition)
restaurants_data = [
    # Ahmedabad
    {'name': 'Taj Palace', 'cuisine': 'North Indian', 'city': 'Ahmedabad', 'delivery_fee': 45},
    {'name': 'The Grand Bhoj', 'cuisine': 'Fine Dining', 'city': 'Ahmedabad', 'delivery_fee': 60},
    {'name': 'Spice Symphony', 'cuisine': 'South Indian', 'city': 'Ahmedabad', 'delivery_fee': 35},
    {'name': 'Royal Rasoi', 'cuisine': 'North Indian', 'city': 'Ahmedabad', 'delivery_fee': 40},
    {'name': 'Saffron Lounge', 'cuisine': 'Mughlai', 'city': 'Ahmedabad', 'delivery_fee': 55},
    {'name': 'Curry Craft', 'cuisine': 'Bengali', 'city': 'Ahmedabad', 'delivery_fee': 30},
    {'name': 'The Dhaba Deluxe', 'cuisine': 'Punjabi', 'city': 'Ahmedabad', 'delivery_fee': 38},
    {'name': 'Masala Magic', 'cuisine': 'Chinese', 'city': 'Ahmedabad', 'delivery_fee': 42},
    {'name': 'Thali Treasures', 'cuisine': 'Gujarati', 'city': 'Ahmedabad', 'delivery_fee': 34},
    {'name': 'Royal Rajdhani', 'cuisine': 'Gujarati', 'city': 'Ahmedabad', 'delivery_fee': 40},

    # Surat
    {'name': 'Biryani Boulevard', 'cuisine': 'Biryani', 'city': 'Surat', 'delivery_fee': 48},
    {'name': 'The Coastal Kitchen', 'cuisine': 'Seafood', 'city': 'Surat', 'delivery_fee': 50},
    {'name': 'Nawab Delight', 'cuisine': 'Awadhi', 'city': 'Surat', 'delivery_fee': 44},
    {'name': 'Tandoor Treasures', 'cuisine': 'Tandoori', 'city': 'Surat', 'delivery_fee': 46},
    {'name': 'The Spice Route', 'cuisine': 'Kerala', 'city': 'Surat', 'delivery_fee': 36},
    {'name': 'Urban Tadka', 'cuisine': 'Street Food', 'city': 'Surat', 'delivery_fee': 32},
    {'name': 'Fusion Flames', 'cuisine': 'Indo-Chinese', 'city': 'Surat', 'delivery_fee': 52},
    {'name': 'The Royal Platter', 'cuisine': 'Maharashtrian', 'city': 'Surat', 'delivery_fee': 39},
    {'name': 'Charcoal Grill', 'cuisine': 'BBQ', 'city': 'Surat', 'delivery_fee': 58},
    {'name': 'Dosa Darbar', 'cuisine': 'South Indian', 'city': 'Surat', 'delivery_fee': 28},

    # Vadodara
    {'name': 'The Curry Club', 'cuisine': 'Multi-Cuisine', 'city': 'Vadodara', 'delivery_fee': 47},
    {'name': 'Bombay Brasserie', 'cuisine': 'Street Food', 'city': 'Vadodara', 'delivery_fee': 41},
    {'name': 'Kebab Factory', 'cuisine': 'Kebabs', 'city': 'Vadodara', 'delivery_fee': 49},
    {'name': 'Chaat Corner Premium', 'cuisine': 'Chaat', 'city': 'Vadodara', 'delivery_fee': 31},
    {'name': 'Biryani House', 'cuisine': 'Biryani', 'city': 'Vadodara', 'delivery_fee': 43},
    {'name': 'Paneer Paradise', 'cuisine': 'Vegetarian', 'city': 'Vadodara', 'delivery_fee': 37},
    {'name': 'Seafood Sensation', 'cuisine': 'Seafood', 'city': 'Vadodara', 'delivery_fee': 54},
    {'name': 'The Vintage Kitchen', 'cuisine': 'Continental', 'city': 'Vadodara', 'delivery_fee': 62},

    # Rajkot
    {'name': 'Spicy Affairs', 'cuisine': 'Andhra', 'city': 'Rajkot', 'delivery_fee': 33},
    {'name': 'Emperor Table', 'cuisine': 'Fine Dining', 'city': 'Rajkot', 'delivery_fee': 65},
    {'name': 'Desi Delights', 'cuisine': 'Punjabi', 'city': 'Rajkot', 'delivery_fee': 35},
    {'name': 'Golden Fork', 'cuisine': 'Continental', 'city': 'Rajkot', 'delivery_fee': 56},
    {'name': 'Moksha Dining', 'cuisine': 'Modern Indian', 'city': 'Rajkot', 'delivery_fee': 59},
    {'name': 'Spice Garden', 'cuisine': 'Kerala', 'city': 'Rajkot', 'delivery_fee': 38},
    {'name': 'Momo Mania Deluxe', 'cuisine': 'Tibetan', 'city': 'Rajkot', 'delivery_fee': 29},

    # Gandhinagar
    {'name': 'The Paratha Place', 'cuisine': 'Punjabi', 'city': 'Gandhinagar', 'delivery_fee': 30},
    {'name': 'Wok This Way', 'cuisine': 'Chinese', 'city': 'Gandhinagar', 'delivery_fee': 51},
    {'name': 'Butter Chicken Co', 'cuisine': 'Punjabi', 'city': 'Gandhinagar', 'delivery_fee': 45},
    {'name': 'Idli Sambar Express', 'cuisine': 'South Indian', 'city': 'Gandhinagar', 'delivery_fee': 27},
    {'name': 'The Rajwada', 'cuisine': 'Rajasthani', 'city': 'Gandhinagar', 'delivery_fee': 53},
    {'name': 'Curry House Deluxe', 'cuisine': 'Multi-Cuisine', 'city': 'Gandhinagar', 'delivery_fee': 48},

    # Himmatnagar
    {'name': 'Sizzler Palace', 'cuisine': 'Continental', 'city': 'Himmatnagar', 'delivery_fee': 57},
    {'name': 'Bombay Sandwich Co', 'cuisine': 'Fast Food', 'city': 'Himmatnagar', 'delivery_fee': 25},
    {'name': 'The Naan Stop', 'cuisine': 'Tandoori', 'city': 'Himmatnagar', 'delivery_fee': 42},

    # Mehsana
    {'name': 'The Coastal Spice', 'cuisine': 'Mangalorean', 'city': 'Mehsana', 'delivery_fee': 36},
    {'name': 'Royal Kathiyawadi', 'cuisine': 'Gujarati', 'city': 'Mehsana', 'delivery_fee': 35},
    {'name': 'Mehsana Delights', 'cuisine': 'North Indian', 'city': 'Mehsana', 'delivery_fee': 40},
]

created_restaurants = []
for i, rest_data in enumerate(restaurants_data):
    slug = rest_data['name'].lower().replace(' ', '-').replace("'", '')
    
    # Coordinates for Gujarat cities
    # Coordinates for Gujarat - Mehsana & Sabarkantha (Himmatnagar)
    base_coords = {
        'Mehsana': (23.5880, 72.3693),
        'Himmatnagar': (23.5979, 72.9698),
    }
    
    # Overwrite city to force all into these two districts
    city = 'Mehsana' if i % 2 == 0 else 'Himmatnagar'
    lat, lng = base_coords[city]
    
    # Add random offset for distinct markers
    final_lat = lat + (random.uniform(-0.05, 0.05))
    final_lng = lng + (random.uniform(-0.05, 0.05))

    defaults = {
        'owner': owners[i],
        'name': rest_data['name'],
        'cuisine': rest_data['cuisine'],
        'description': f"Premium {rest_data['cuisine']} restaurant offering authentic flavors and exceptional dining experience",
        'address': f"{i+1}, Station Road, {city}, Gujarat",
        'city': city,
        'state': 'Gujarat',
        'pincode': f'380{i:03d}',
        'latitude': final_lat,
        'longitude': final_lng,
        'phone': f'+91{8000000000 + i}',
        'delivery_fee': Decimal(str(rest_data['delivery_fee'])),
        'delivery_time': random.randint(25, 45),
        'rating': round(random.uniform(3.8, 4.9), 1),
        'is_active': True,
        'status': 'APPROVED',
    }

    restaurant, created = Restaurant.objects.get_or_create(
        slug=slug,
        defaults=defaults
    )
    
    # FORCE UPDATE if already exists (to apply Location Changes)
    if not created:
        print(f'  Updating location for: {restaurant.name} -> {city}, Gujarat')
        restaurant.city = defaults['city']
        restaurant.state = defaults['state']
        restaurant.address = defaults['address']
        restaurant.latitude = defaults['latitude']
        restaurant.longitude = defaults['longitude']
        restaurant.pincode = defaults['pincode']
        restaurant.cuisine = defaults['cuisine']
        restaurant.save()
    else:
        print(f'  Created restaurant: {restaurant.name} in {city}')

    created_restaurants.append((restaurant, rest_data['cuisine']))

print(f"\nProcessing {len(created_restaurants)} restaurants")

# Menu items with Indian dishes
menu_items = [
    ('Butter Chicken', 'Tender chicken in creamy tomato gravy', 'NON_VEG', 320, 25),
    ('Dal Makhani', 'Black lentils slow-cooked with butter', 'VEG', 240, 20),
    ('Paneer Tikka Masala', 'Grilled cottage cheese in spiced gravy', 'VEG', 280, 22),
    ('Tandoori Chicken', 'Marinated chicken grilled in clay oven', 'NON_VEG', 380, 25),
    ('Palak Paneer', 'Cottage cheese in creamy spinach', 'VEG', 250, 20),
    ('Chicken Biryani', 'Fragrant basmati rice with tender chicken', 'NON_VEG', 350, 35),
    ('Garlic Naan', 'Soft bread with garlic and butter', 'VEG', 60, 10),
    ('Masala Dosa', 'Crispy rice crepe with spiced potato filling', 'VEG', 120, 15),
    ('Idli Sambar', 'Steamed rice cakes with lentil soup', 'VEG', 80, 12),
    ('Chicken Tikka', 'Grilled chicken pieces marinated in yogurt', 'NON_VEG', 340, 22),
    ('Veg Biryani', 'Fragrant rice with mixed vegetables', 'VEG', 250, 25),
    ('Mutton Rogan Josh', 'Aromatic lamb curry with Kashmiri spices', 'NON_VEG', 420, 30),
    ('Hakka Noodles', 'Stir-fried noodles with vegetables', 'VEG', 180, 15),
    ('Chilli Chicken', 'Spicy chicken with bell peppers', 'NON_VEG', 280, 20),
    ('Fried Rice', 'Stir-fried rice with vegetables', 'VEG', 160, 15),
]

# Add menu items to each restaurant
total_items = 0
for restaurant, cuisine in created_restaurants:
    items_added = 0
    # Add 10-12 random items to each restaurant
    selected_items = random.sample(menu_items, min(12, len(menu_items)))
    
    for item_data in selected_items:
        name, desc, veg_type, price, prep_time = item_data
        menu_item, created = MenuItem.objects.get_or_create(
            restaurant=restaurant,
            name=name,
            defaults={
                'description': desc,
                'price': Decimal(str(price)),
                'category': None,  # Category is ForeignKey, set to None
                'veg_type': veg_type,
                'is_available': True,
                'preparation_time': prep_time,
            }
        )
        if created:
            items_added += 1
            total_items += 1
    
    print(f'  Added {items_added} items to {restaurant.name}')

print(f"\n{'='*60}")
print(f"🎉 SUCCESS! Database seeded with:")
print(f"   - {len(created_restaurants)} Premium Restaurants")
print(f"   - {total_items} Menu Items")
print(f"   - Delivery fees ranging from ₹{min(r['delivery_fee'] for r in restaurants_data)} to ₹{max(r['delivery_fee'] for r in restaurants_data)}")
print(f"{'='*60}")
print(f"\n✅ Now refresh your browser at http://localhost:3000 to see all restaurants!")
