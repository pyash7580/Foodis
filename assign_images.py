import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from restaurant.models import Restaurant
from client.models import MenuItem

COVER_DIR = r'd:\Foodis\media\restaurants\covers'

if not os.path.exists(COVER_DIR):
    print("Cover directory not found:", COVER_DIR)
    exit(1)

files = [f for f in os.listdir(COVER_DIR) if os.path.isfile(os.path.join(COVER_DIR, f))]
if not files:
    print("No images found in", COVER_DIR)
    exit(1)

# Paths relative to MEDIA_ROOT
image_paths = [f'restaurants/covers/{f}' for f in files]

# Fix 1: Ensure exactly 48 restaurants are shown
# Get all restaurants
restaurants = Restaurant.objects.all().order_by('id')
# Set first 48 to active, rest inactive
for i, r in enumerate(restaurants):
    if i < 48:
        # It's one of the 48 to be active
        r.is_active = True
        r.status = 'APPROVED'
        
        # Pick a random image for the restaurant
        img = random.choice(image_paths)
        if hasattr(r, 'image'):
            r.image = img
        if hasattr(r, 'image_url'):
            r.image_url = '' # clear url so it uses local image
        if hasattr(r, 'cover_image'):
            r.cover_image = img
        
        r.save()
        
        # Now update its menu items
        menu_items = MenuItem.objects.filter(restaurant=r)
        for item in menu_items:
            dish_img = random.choice(image_paths)
            if hasattr(item, 'image'):
                item.image = dish_img
            if hasattr(item, 'image_url'):
                item.image_url = ''
            item.save()
    else:
        # Set inactive
        r.is_active = False
        r.save()

print(f"Successfully updated 48 restaurants and their menu items with images from {COVER_DIR}")
