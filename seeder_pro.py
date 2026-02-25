import os
import django
import random
import string
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from django.contrib.auth import get_user_model
from client.models import Restaurant, MenuItem, Category
from rider.models import Rider
from django.db import transaction

User = get_user_model()

def generate_phone():
    return f"+91{random.randint(6000000000, 9999999999)}"

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

@transaction.atomic
def run_seeder():
    print("🚀 Starting Production Seeder Pro...")

    # 1. Categories
    print("Step 1: Creating Categories...")
    categories_list = ['North Indian', 'South Indian', 'Chinese', 'Desserts', 'Beverages', 'Fast Food', 'Pizzas', 'Street Food', 'Gujarati', 'Biryani']
    cat_objs = []
    for cat_name in categories_list:
        slug = cat_name.lower().replace(' ', '-')
        cat, _ = Category.objects.get_or_create(name=cat_name, defaults={'slug': slug})
        cat_objs.append(cat)

    # 2. Restaurants (48)
    print("Step 2: Creating 48 Premium Restaurants...")
    restaurant_names = [
        'Taj Palace', 'The Grand Bhoj', 'Spice Symphony', 'Royal Rasoi', 'Saffron Lounge',
        'Curry Craft', 'The Dhaba Deluxe', 'Masala Magic', 'Thali Treasures', 'Royal Rajdhani',
        'Biryani Boulevard', 'The Coastal Kitchen', 'Nawab Delight', 'Tandoor Treasures', 'The Spice Route',
        'Urban Tadka', 'Fusion Flames', 'The Royal Platter', 'Charcoal Grill', 'Dosa Darbar',
        'The Curry Club', 'Bombay Brasserie', 'Kebab Factory', 'Chaat Corner Premium', 'Biryani House',
        'Paneer Paradise', 'Seafood Sensation', 'The Vintage Kitchen', 'Spicy Affairs', 'Emperor Table',
        'Desi Delights', 'Golden Fork', 'Moksha Dining', 'Spice Garden', 'Momo Mania Deluxe',
        'The Paratha Place', 'Wok This Way', 'Butter Chicken Co', 'Idli Sambar Express', 'The Rajwada',
        'Curry House Deluxe', 'Sizzler Palace', 'Bombay Sandwich Co', 'The Naan Stop', 'The Coastal Spice',
        'Royal Kathiyawadi', 'Mehsana Delights', 'Himmatnagar Hub'
    ]

    cuisines = ['North Indian', 'South Indian', 'Chinese', 'Desserts', 'Fast Food', 'Pizzas', 'Street Food', 'Gujarati', 'Biryani', 'Mughlai']
    cities = ['Ahmedabad', 'Surat', 'Vadodara', 'Rajkot', 'Gandhinagar', 'Himmatnagar', 'Mehsana']

    owners = []
    for i in range(48):
        email = f'owner{i+1}@foodis.com'
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'phone': f'+9171{i:08d}',
                'name': f'Owner {i+1}',
                'role': 'RESTAURANT',
                'is_active': True,
                'is_verified': True
            }
        )
        if created:
            user.set_password('password123')
            user.save()
        owners.append(user)

    for i, name in enumerate(restaurant_names):
        slug = name.lower().replace(' ', '-').replace("'", "")
        city = cities[i % len(cities)]
        cuisine = random.choice(cuisines)
        
        # Coordinates approx for Gujarat
        lat = random.uniform(21.0, 24.0)
        lng = random.uniform(70.0, 73.0)

        r, created = Restaurant.objects.get_or_create(
            slug=slug,
            defaults={
                'name': name,
                'owner': owners[i],
                'cuisine': cuisine,
                'description': f"Premium {cuisine} restaurant in {city}.",
                'address': f"Street {i+1}, {city}, Gujarat",
                'city': city,
                'state': 'Gujarat',
                'pincode': f'380{i:03d}',
                'latitude': lat,
                'longitude': lng,
                'phone': f'+9181{i:08d}',
                'delivery_fee': Decimal(random.randint(20, 60)),
                'delivery_time': random.randint(20, 50),
                'rating': round(random.uniform(3.5, 4.9), 1),
                'is_active': True,
                'status': 'APPROVED'
            }
        )
        if not created:
            r.status = 'APPROVED'
            r.is_active = True
            r.save()

        # Menu Items (10 per restaurant)
        for j in range(10):
            MenuItem.objects.get_or_create(
                restaurant=r,
                name=f"Dish {j+1} from {name}",
                defaults={
                    'description': f"Delicious dish prepared by {name}",
                    'price': Decimal(random.randint(100, 500)),
                    'veg_type': random.choice(['VEG', 'NON_VEG', 'EGG']),
                    'category': random.choice(cat_objs),
                    'is_available': True
                }
            )

    # 3. Riders (300)
    print("Step 3: Creating 300 Riders...")
    rider_names = ["Rider " + str(i+1) for i in range(300)]
    
    for i in range(300):
        phone = f"92{i:08d}" # 10 digits
        clean_phone = phone
        
        user, created = User.objects.get_or_create(
            phone=clean_phone,
            defaults={
                'name': f"Premium Rider {i+1}",
                'email': f"rider{i+1}@foodis.com",
                'role': 'RIDER',
                'is_active': True,
                'is_verified': True
            }
        )
        if created:
            user.set_password('password123')
            user.save()

        # Rider Profile (rider.models.Rider)
        city = random.choice(cities)
        rider_profile, r_created = Rider.objects.get_or_create(
            phone=clean_phone,
            defaults={
                'full_name': user.name,
                'city': city,
                'is_active': True,
                'status': 'ONLINE',
                'is_online': True,
                'wallet_balance': Decimal(random.randint(0, 1000))
            }
        )
        if not r_created:
            rider_profile.status = 'ONLINE'
            rider_profile.is_online = True
            rider_profile.save()

    print("\n✅ Seeding Complete!")
    print(f"Restaurants: {Restaurant.objects.count()}")
    print(f"Riders: {Rider.objects.count()}")
    print(f"Users: {User.objects.count()}")

if __name__ == "__main__":
    run_seeder()
