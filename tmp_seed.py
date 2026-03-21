import django
import os
import sys
from decimal import Decimal

# Setup Django environment
sys.path.append(r'd:\Foodis')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from client.models import Category, Restaurant, MenuItem

def seed_data():
    categories_data = [
        {'name': 'Pizza', 'slug': 'pizza'},
        {'name': 'Biryani', 'slug': 'biryani'},
        {'name': 'Burger', 'slug': 'burger'},
        {'name': 'Chinese', 'slug': 'chinese'},
        {'name': 'Healthy', 'slug': 'healthy'},
        {'name': 'Dessert', 'slug': 'dessert'},
    ]

    dishes_data = {
        'Pizza': [
            {'name': 'Margherita Pizza', 'desc': 'Classic cheese and tomato pizza', 'price': 299, 'veg': 'VEG'},
            {'name': 'Pepperoni Pizza', 'desc': 'Spicy pepperoni with mozzarella', 'price': 399, 'veg': 'NON_VEG'},
        ],
        'Biryani': [
            {'name': 'Hyderabadi Chicken Biryani', 'desc': 'Authentic dum biryani with tender chicken', 'price': 250, 'veg': 'NON_VEG'},
            {'name': 'Veg Dum Biryani', 'desc': 'Aromatic rice with mixed vegetables', 'price': 200, 'veg': 'VEG'},
        ],
        'Burger': [
            {'name': 'Classic Veggie Burger', 'desc': 'Crispy veg patty with fresh lettuce', 'price': 149, 'veg': 'VEG'},
            {'name': 'Double Cheese Chicken Burger', 'desc': 'Juicy chicken patty with double cheese', 'price': 199, 'veg': 'NON_VEG'},
        ],
        'Chinese': [
            {'name': 'Veg Hakka Noodles', 'desc': 'Wok-tossed noodles with veggies', 'price': 180, 'veg': 'VEG'},
            {'name': 'Chilli Chicken', 'desc': 'Spicy diced chicken in soy sauce', 'price': 220, 'veg': 'NON_VEG'},
        ],
        'Healthy': [
            {'name': 'Quinoa Power Salad', 'desc': 'Healthy quinoa with avocado and greens', 'price': 249, 'veg': 'VEG'},
            {'name': 'Grilled Chicken Breast', 'desc': 'Lean protein with steamed veggies', 'price': 299, 'veg': 'NON_VEG'},
        ],
        'Dessert': [
            {'name': 'Chocolate Lava Cake', 'desc': 'Warm chocolate cake with a gooey center', 'price': 120, 'veg': 'VEG'},
            {'name': 'New York Cheesecake', 'desc': 'Classic baked cheesecake slice', 'price': 180, 'veg': 'VEG'},
        ]
    }

    # 1. Create Categories
    category_objs = {}
    for cat in categories_data:
        obj, created = Category.objects.get_or_create(
            name=cat['name'],
            defaults={'slug': cat['slug'], 'is_active': True}
        )
        category_objs[cat['name']] = obj
        print(f"[{'CREATED' if created else 'EXISTS'}] Category: {cat['name']}")

    # 2. Get some approved restaurants
    restaurants = list(Restaurant.objects.filter(status='APPROVED', is_active=True)[:5])
    if not restaurants:
        print("No approved restaurants found. Please add or approve some restaurants first.")
        return

    # 3. Add dishes to restaurants
    dishes_added = 0
    for restaurant in restaurants:
        print(f"\nAdding dishes to {restaurant.name}...")
        for cat_name, dishes in dishes_data.items():
            cat_obj = category_objs[cat_name]
            for dish in dishes:
                obj, created = MenuItem.objects.get_or_create(
                    restaurant=restaurant,
                    name=dish['name'],
                    defaults={
                        'description': dish['desc'],
                        'price': Decimal(dish['price']),
                        'veg_type': dish['veg'],
                        'category': cat_obj,
                        'is_available': True
                    }
                )
                if created:
                    dishes_added += 1
                    print(f"  + Added: {dish['name']} ({cat_name})")

    print(f"\nSuccess! Added {dishes_added} new dishes across {len(restaurants)} restaurants.")

if __name__ == '__main__':
    seed_data()
