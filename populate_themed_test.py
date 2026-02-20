import os
import sys

# Set up Django environment without importing heavy packages initially
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')

# Disable OpenBLAS threading to avoid memory issues
os.environ['OPENBLAS_NUM_THREADS'] = '1'

import django
django.setup()

from client.models import Restaurant, MenuItem
from decimal import Decimal

# Restaurant-specific themed menu items (partial list for testing)
THEMED_MENUS = {
    'Idli Sambar Express': [
        ('Idli (3 pcs)', 'Soft steamed rice cakes served with sambar and chutneys', 'VEG', 60, 10),
        ('Medu Vada (2 pcs)', 'Crispy lentil donuts with sambar', 'VEG', 70, 12),
        ('Masala Dosa', 'Crispy rice crepe filled with spiced potato filling', 'VEG', 90, 15),
        ('Plain Dosa', 'Thin crispy rice crepe', 'VEG', 70, 12),
        ('Rava Dosa', 'Crispy semolina crepe', 'VEG', 85, 15),
        ('Onion Uttapam', 'Thick rice pancake with onion topping', 'VEG', 80, 15),
        ('Sambar Rice', 'Rice mixed with tangy lentil stew', 'VEG', 95, 18),
        ('Curd Rice', 'Soothing rice with yogurt and tempering', 'VEG', 75, 10),
        ('Filter Coffee', 'Authentic South Indian filter coffee', 'VEG', 40, 5),
        ('Coconut Chutney', 'Fresh coconut chutney', 'VEG', 20, 5),
    ],
    'Dosa Darbar': [
        ('Mysore Masala Dosa', 'Spicy dosa with red chutney and potato filling', 'VEG', 110, 18),
        ('Cheese Dosa', 'Dosa topped with melted cheese', 'VEG', 120, 15),
        ('Paneer Dosa', 'Dosa filled with spiced paneer', 'VEG', 130, 18),
        ('Ghee Roast Dosa', 'Crispy dosa roasted in pure ghee', 'VEG', 100, 15),
        ('Paper Dosa', 'Extra thin and crispy large dosa', 'VEG', 95, 18),
        ('Spring Dosa', 'Dosa with mixed vegetable filling', 'VEG', 115, 20),
        ('Set Dosa (3 pcs)', 'Soft fluffy mini dosas', 'VEG', 90, 15),
        ('Rava Masala Dosa', 'Semolina dosa with potato filling', 'VEG', 105, 18),
        ('Podi Dosa', 'Dosa with spicy gun powder', 'VEG', 85, 15),
        ('Butter Dosa', 'Crispy dosa with generous butter', 'VEG', 90, 15),
    ],
}

def populate_sample_themed_dishes():
    """Populate sample restaurants with themed dishes"""
    print("Starting to populate themed dishes for sample restaurants...\\n")
    
    for restaurant_name, menu_items in THEMED_MENUS.items():
        try:
            restaurant = Restaurant.objects.filter(name__iexact=restaurant_name).first()
            
            if not restaurant:
                print(f"Restaurant '{restaurant_name}' not found. Skipping...")
                continue
            
            # Clear existing items
            deleted = MenuItem.objects.filter(restaurant=restaurant).delete()[0]
            print(f"Deleted {deleted} old items from {restaurant.name}")
            
            # Add new themed items
            for name, desc, veg_type, price, prep_time in menu_items:
                MenuItem.objects.create(
                    restaurant=restaurant,
                    name=name,
                    description=desc,
                    price=Decimal(str(price)),
                    category=None,
                    veg_type=veg_type,
                    is_available=True,
                    preparation_time=prep_time,
                )
            
            print(f"Added {len(menu_items)} themed dishes to {restaurant.name}")
            
        except Exception as e:
            print(f"Error processing {restaurant_name}: {str(e)}")
    
    print("\\nDone!")

if __name__ == '__main__':
    populate_sample_themed_dishes()
