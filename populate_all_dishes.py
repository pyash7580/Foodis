#!/usr/bin/env python
import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from client.models import Restaurant, MenuItem, Category

print("=" * 80)
print("POPULATING DATABASE WITH ALL DISHES FROM LIST")
print("=" * 80)

# Mapping of restaurants from the list to those in database (matching by name)
restaurant_mapping = {
    'Chaat Corner Premium': 'Chaat Corner Premium',
    'Kebab Factory': 'Kebab Factory',
    'Kebab Factory (2)': 'Kebab Factory (2)',
    'Naan Basket': 'Naan Basket',
    'popes cafe': 'popes cafe',
    'Spice Symphony': 'Spice Symphony',
    'Taj Palace': 'Taj Palace',
    'Tandoor Treasures': 'Tandoor Treasures',
    'Thali Treasures': 'Thali Treasures',
    'The Coastal Spice': 'The Coastal Spice',
    'The Curry Club': 'The Curry Club',
    'The Dhaba Deluxe': 'The Dhaba Deluxe',
    'The Naan Stop': 'The Naan Stop',
    'The Rajwada': 'The Rajwada',
    'The Spice Route': 'The Spice Route',
    'The Vintage Kitchen': 'The Vintage Kitchen',
    'Wok This Way': 'Wok This Way',
}

# All dishes data from your list
all_dishes_by_restaurant = {
    'Chaat Corner Premium': [
        ('Aloo Tikki Chaat', 'VEG', 90.00),
        ('Basket Chaat', 'VEG', 120.00),
        ('Dahi Puri', 'VEG', 80.00),
        ('Dahi Vada', 'VEG', 90.00),
        ('Palak Patta Chaat', 'VEG', 100.00),
        ('Pani Puri (6 pcs)', 'VEG', 60.00),
        ('Papdi Chaat', 'VEG', 80.00),
        ('Raj Kachori', 'VEG', 110.00),
        ('Samosa Chaat', 'VEG', 90.00),
        ('Sev Puri', 'VEG', 70.00),
    ],
    'Kebab Factory': [
        ('Chicken Malai Tikka', 'NON_VEG', 340.00),
        ('Galouti Kebab', 'NON_VEG', 380.00),
        ('Kakori Kebab', 'NON_VEG', 360.00),
        ('Kebab Platter', 'NON_VEG', 650.00),
        ('Mutton Burra', 'NON_VEG', 420.00),
        ('Reshmi Kebab', 'NON_VEG', 330.00),
        ('Shami Kebab', 'NON_VEG', 320.00),
        ('Veg Seekh Kebab', 'VEG', 240.00),
    ],
    'Kebab Factory (2)': [
        ('Chicken Malai Tikka', 'NON_VEG', 340.00),
        ('Galouti Kebab', 'NON_VEG', 380.00),
        ('Kakori Kebab', 'NON_VEG', 360.00),
        ('Kebab Platter', 'NON_VEG', 650.00),
        ('Mutton Burra', 'NON_VEG', 420.00),
        ('Reshmi Kebab', 'NON_VEG', 330.00),
        ('Shami Kebab', 'NON_VEG', 320.00),
        ('Veg Seekh Kebab', 'VEG', 240.00),
    ],
    'Naan Basket': [
        ('Butter Naan', 'VEG', 50.00),
        ('Cheese Naan', 'VEG', 90.00),
        ('Garlic Naan', 'VEG', 60.00),
        ('Keema Naan', 'NON_VEG', 120.00),
        ('Lachha Paratha', 'VEG', 70.00),
        ('Naan Basket (Assorted)', 'VEG', 180.00),
        ('Peshawari Naan', 'VEG', 100.00),
        ('Tandoori Roti', 'VEG', 30.00),
    ],
    'popes cafe': [
        ('Brownie with Ice Cream', 'VEG', 160.00),
        ('Cappuccino', 'VEG', 120.00),
        ('Cheese Burger', 'VEG', 170.00),
        ('Cheesecake Slice', 'VEG', 180.00),
        ('Chicken BBQ Pizza (8")', 'NON_VEG', 340.00),
        ('Chicken Burger', 'NON_VEG', 200.00),
        ('Chicken Wings (6 pcs)', 'NON_VEG', 240.00),
        ('Classic Burger', 'VEG', 140.00),
        ('Club Sandwich', 'VEG', 150.00),
        ('Cold Coffee', 'VEG', 150.00),
        ('Espresso', 'VEG', 80.00),
        ('French Fries', 'VEG', 90.00),
        ('Grilled Chicken Sandwich', 'NON_VEG', 180.00),
        ('Hot Chocolate', 'VEG', 140.00),
        ('Latte', 'VEG', 130.00),
        ('Margherita Pizza (8")', 'VEG', 250.00),
        ('Nachos with Cheese Dip', 'VEG', 170.00),
        ('Onion Rings', 'VEG', 120.00),
        ('Panini Sandwich', 'VEG', 160.00),
        ('Pepperoni Pizza (8")', 'NON_VEG', 360.00),
        ('Veg Supreme Burger', 'VEG', 160.00),
        ('Veg Supreme Pizza (8")', 'VEG', 300.00),
        ('Waffles', 'VEG', 190.00),
    ],
    'Spice Symphony': [
        ('Appam (2 pcs)', 'VEG', 80.00),
        ('Bengali Fish Curry', 'NON_VEG', 340.00),
        ('Butter Naan', 'VEG', 50.00),
        ('Chettinad Chicken', 'NON_VEG', 350.00),
        ('Chettinad Veg Curry', 'VEG', 240.00),
        ('Dal Tadka', 'VEG', 190.00),
        ('Goan Fish Curry', 'NON_VEG', 360.00),
        ('Hyderabadi Chicken Curry', 'NON_VEG', 340.00),
        ('Kolhapuri Mutton', 'NON_VEG', 430.00),
        ('Paneer Tikka Masala', 'VEG', 280.00),
        ('Punjabi Chicken Curry', 'NON_VEG', 320.00),
        ('Rajasthani Laal Maas', 'NON_VEG', 450.00),
        ('Steamed Rice', 'VEG', 80.00),
    ],
    'Taj Palace': [
        ('Butter Chicken', 'NON_VEG', 360.00),
        ('Chicken Seekh Kebab', 'NON_VEG', 340.00),
        ('Dal Makhani', 'VEG', 260.00),
        ('Gulab Jamun (2 pcs)', 'VEG', 80.00),
        ('Naan Basket', 'VEG', 160.00),
        ('Paneer Butter Masala', 'VEG', 300.00),
        ('Paneer Tikka', 'VEG', 300.00),
        ('Rogan Josh', 'NON_VEG', 450.00),
        ('Shahi Tukda', 'VEG', 130.00),
        ('Tandoori Murgh Full', 'NON_VEG', 680.00),
    ],
    'Tandoor Treasures': [
        ('Afghani Chicken', 'NON_VEG', 360.00),
        ('Chicken Tikka', 'NON_VEG', 320.00),
        ('Fish Tikka', 'NON_VEG', 380.00),
        ('Hara Bhara Kebab', 'VEG', 220.00),
        ('Paneer Tikka', 'VEG', 280.00),
        ('Seekh Kebab', 'NON_VEG', 340.00),
        ('Tandoori Chicken Half', 'NON_VEG', 350.00),
        ('Tandoori Mushroom', 'VEG', 260.00),
        ('Tandoori Prawns', 'NON_VEG', 480.00),
    ],
    'Thali Treasures': [
        ('Dhokla', 'VEG', 60.00),
        ('Gujarati Thali', 'VEG', 280.00),
        ('Kathiyawadi Thali', 'VEG', 300.00),
        ('Khandvi', 'VEG', 80.00),
        ('Mini Thali', 'VEG', 180.00),
        ('North Indian Thali', 'VEG', 280.00),
        ('Rajasthani Thali', 'VEG', 320.00),
        ('South Indian Thali', 'VEG', 260.00),
        ('Undhiyu', 'VEG', 160.00),
    ],
    'The Coastal Spice': [
        ('Appam (2 pcs)', 'VEG', 80.00),
        ('Avial', 'VEG', 220.00),
        ('Chettinad Chicken', 'NON_VEG', 340.00),
        ('Chicken Cafreal', 'NON_VEG', 330.00),
        ('Kerala Parotta with Beef Fry', 'NON_VEG', 320.00),
        ('Malabar Fish Curry', 'NON_VEG', 360.00),
        ('Malabar Parotta', 'VEG', 60.00),
        ('Mutton Stew', 'NON_VEG', 380.00),
        ('Neer Dosa (3 pcs)', 'VEG', 90.00),
        ('Prawn Ghee Roast', 'NON_VEG', 420.00),
        ('Sol Kadhi', 'VEG', 70.00),
        ('Vegetable Stew', 'VEG', 240.00),
    ],
    'The Curry Club': [
        ('Butter Naan', 'VEG', 50.00),
        ('Chicken Tikka Masala', 'NON_VEG', 340.00),
        ('Club Special Butter Chicken', 'NON_VEG', 360.00),
        ('Dal Makhani', 'VEG', 240.00),
        ('Fish Curry Bengali Style', 'NON_VEG', 350.00),
        ('Garlic Naan', 'VEG', 60.00),
        ('Kadhai Paneer', 'VEG', 270.00),
        ('Lamb Rogan Josh', 'NON_VEG', 450.00),
        ('Malai Kofta', 'VEG', 280.00),
        ('Mixed Veg Curry', 'VEG', 220.00),
        ('Palak Paneer', 'VEG', 260.00),
        ('Paneer Tikka Masala', 'VEG', 280.00),
        ('Prawn Malai Curry', 'NON_VEG', 420.00),
    ],
    'The Dhaba Deluxe': [
        ('Aloo Paratha', 'VEG', 70.00),
        ('Amritsari Kulcha', 'VEG', 80.00),
        ('Chole Bhature', 'VEG', 140.00),
        ('Dal Tadka', 'VEG', 180.00),
        ('Highway Chicken Curry', 'NON_VEG', 280.00),
        ('Lassi (Sweet/Salted)', 'VEG', 60.00),
        ('Makki Ki Roti', 'VEG', 40.00),
        ('Mixed Veg', 'VEG', 160.00),
        ('Sarson Ka Saag', 'VEG', 200.00),
    ],
    'The Naan Stop': [
        ('Butter Naan', 'VEG', 50.00),
        ('Cheese Naan', 'VEG', 90.00),
        ('Garlic Naan', 'VEG', 60.00),
        ('Keema Naan', 'NON_VEG', 120.00),
        ('Lachha Paratha', 'VEG', 70.00),
        ('Naan Basket (Assorted)', 'VEG', 180.00),
        ('Peshawari Naan', 'VEG', 100.00),
        ('Tandoori Roti', 'VEG', 30.00),
    ],
    'The Rajwada': [
        ('Bajre Ki Roti', 'VEG', 35.00),
        ('Dal Baati Churma', 'VEG', 280.00),
        ('Gatte Ki Sabzi', 'VEG', 220.00),
        ('Ghevar', 'VEG', 150.00),
        ('Jungli Maas', 'NON_VEG', 490.00),
        ('Ker Sangri', 'VEG', 240.00),
        ('Mawa Kachori', 'VEG', 90.00),
        ('Mirchi Vada', 'VEG', 120.00),
        ('Rajasthani Laal Maas', 'NON_VEG', 480.00),
        ('Safed Maas', 'NON_VEG', 460.00),
    ],
    'The Spice Route': [
        ('Appam (3 pcs)', 'VEG', 90.00),
        ('Awadhi Chicken Korma', 'NON_VEG', 360.00),
        ('Bengali Aloo Posto', 'VEG', 200.00),
        ('Delhi Style Butter Chicken', 'NON_VEG', 340.00),
        ('Gujarati Undhiyu', 'VEG', 240.00),
        ('Kashmiri Mutton', 'NON_VEG', 440.00),
        ('Kerala Fish Curry', 'NON_VEG', 350.00),
        ('Maharashtra Pithla Bhakri', 'VEG', 160.00),
        ('Malabar Parotta', 'VEG', 60.00),
        ('Mangalorean Prawn Curry', 'NON_VEG', 400.00),
        ('Punjabi Chole', 'VEG', 180.00),
        ('Rajasthani Chicken', 'NON_VEG', 330.00),
        ('South Indian Sambar', 'VEG', 120.00),
    ],
    'The Vintage Kitchen': [
        ('Apple Pie', 'VEG', 150.00),
        ('Bread Pudding', 'VEG', 120.00),
        ('British Raj Chicken Curry', 'NON_VEG', 350.00),
        ('Chicken Cutlet', 'NON_VEG', 240.00),
        ('Club Sandwich', 'VEG', 180.00),
        ('Cottage Cheese Steak', 'VEG', 290.00),
        ('Creamy Mushroom Soup', 'VEG', 150.00),
        ('Fish & Chips', 'NON_VEG', 360.00),
        ('Mashed Potatoes', 'VEG', 100.00),
        ('Railway Mutton Curry', 'NON_VEG', 420.00),
        ("Shepherd's Pie", 'NON_VEG', 380.00),
        ('Veg Cutlet', 'VEG', 180.00),
    ],
    'Wok This Way': [
        ('Chicken Fried Rice', 'NON_VEG', 190.00),
        ('Chicken Hakka Noodles', 'NON_VEG', 200.00),
        ('Chilli Chicken', 'NON_VEG', 280.00),
        ('Manchurian (Dry/Gravy)', 'VEG', 180.00),
        ('Schezwan Noodles', 'VEG', 170.00),
        ('Spring Rolls', 'VEG', 140.00),
        ('Veg Fried Rice', 'VEG', 150.00),
        ('Veg Hakka Noodles', 'VEG', 160.00),
    ],
}

# Get or create categories
print("\nCreating food categories...")
category_names = ['North Indian', 'South Indian', 'Chinese', 'Desserts', 'Pizza', 'Biryani',
                  'Fast Food', 'Mughlai', 'Street Food', 'Seafood', 'Tandoori', 'Gujarati',
                  'Beverages', 'Bread', 'Rice', 'Curry', 'Appetizers']
categories = {}
for cat_name in category_names:
    cat, created = Category.objects.get_or_create(
        name=cat_name,
        defaults={'slug': cat_name.lower().replace(' ', '-')}
    )
    categories[cat_name] = cat

print(f"[OK] Created/found {len(categories)} categories")

# Delete existing menu items for our restaurants
print("\nClearing existing menu items for our restaurants...")
count = 0
for db_name in restaurant_mapping.values():
    try:
        rest = Restaurant.objects.get(name=db_name)
        count += rest.menu_items.count()
        rest.menu_items.all().delete()
    except Restaurant.DoesNotExist:
        pass
print(f"[OK] Deleted {count} existing menu items")

# Populate all dishes
print("\nPopulating all dishes...")
total_dishes_created = 0
restaurants_updated = 0

for list_name, db_name in restaurant_mapping.items():
    if list_name not in all_dishes_by_restaurant:
        print(f"  [SKIP] No dishes found for: {list_name}")
        continue

    try:
        restaurant = Restaurant.objects.get(name=db_name)
        dishes = all_dishes_by_restaurant[list_name]

        for dish_name, veg_type, price in dishes:
            # Determine category based on dish name
            category = None
            dish_lower = dish_name.lower()

            if 'biryani' in dish_lower:
                category = categories.get('Biryani') or categories.get('North Indian')
            elif 'naan' in dish_lower or 'roti' in dish_lower or 'paratha' in dish_lower:
                category = categories.get('Bread') or categories.get('North Indian')
            elif 'curry' in dish_lower:
                category = categories.get('Curry') or categories.get('North Indian')
            elif 'tandoori' in dish_lower or 'tikka' in dish_lower or 'kebab' in dish_lower:
                category = categories.get('Tandoori') or categories.get('Appetizers')
            elif 'dosa' in dish_lower:
                category = categories.get('South Indian') or categories.get('Bread')
            elif 'pizza' in dish_lower:
                category = categories.get('Pizza') or categories.get('Mughlai')
            elif 'burger' in dish_lower or 'sandwich' in dish_lower or 'fries' in dish_lower:
                category = categories.get('Fast Food')
            elif 'coffee' in dish_lower or 'cappuccino' in dish_lower or 'latte' in dish_lower:
                category = categories.get('Beverages')
            elif any(x in dish_lower for x in ['thali', 'chaat', 'puri', 'samosa', 'vada']):
                category = categories.get('Street Food') or categories.get('North Indian')
            else:
                category = categories.get('North Indian')

            # Create menu item
            MenuItem.objects.get_or_create(
                restaurant=restaurant,
                name=dish_name,
                defaults={
                    'description': f"Authentic {dish_name}",
                    'price': Decimal(str(price)),
                    'veg_type': veg_type,
                    'category': category,
                    'is_available': True,
                    'preparation_time': 20,
                }
            )
            total_dishes_created += 1

        print(f"  [OK] {db_name}: {len(dishes)} dishes added")
        restaurants_updated += 1

    except Restaurant.DoesNotExist:
        print(f"  [ERROR] Restaurant not found: {db_name}")

print("\n" + "=" * 80)
print(f"[OK] SUCCESS! Database populated with all dishes")
print("=" * 80)
print(f"\nDetails:")
print(f"  - Restaurants updated: {restaurants_updated}")
print(f"  - Total dishes created: {total_dishes_created}")
print(f"\nNow test on your site:")
print(f"  1. Visit: http://localhost:3000/client")
print(f"  2. Click on any restaurant")
print(f"  3. All dishes should now show in the menu")
print("=" * 80)
