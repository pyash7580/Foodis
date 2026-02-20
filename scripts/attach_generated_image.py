import sys
import os
import django
from django.core.files import File
from django.conf import settings

# Setup Django environment
# Add project root to sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from client.models import MenuItem, Restaurant, Category

def attach_image(dish_name, image_path):
    print(f"Processing Dish: '{dish_name}'")
    print(f"Image Source: '{image_path}'")
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return

    # Clean name
    dish_name_clean = dish_name.strip()
    
    # Check if dish exists (case-insensitive)
    items = MenuItem.objects.filter(name__iexact=dish_name_clean)
    
    if items.exists():
        item = items.first()
        print(f"Found existing dish: '{item.name}' (ID: {item.id})")
        print(f"Restaurant: {item.restaurant.name}")
    else:
        print(f"Dish '{dish_name_clean}' not found. Creating new entry...")
        # Get a default restaurant - Try 'Main' or first available
        restaurant = Restaurant.objects.first()
        if not restaurant:
            print("Error: No restaurants found in database to attach dish to.")
            return
            
        # Create new item
        item = MenuItem(
            name=dish_name_clean,
            restaurant=restaurant,
            price=299.00,  # Default price
            description=f"Freshly prepared {dish_name_clean}",
            veg_type='VEG', # Default
            is_available=True
        )
        print(f"Creating for restaurant: {restaurant.name}")

    # Prepare filename
    # The prompt requests: dish-name-lowercase-with-dashes.png
    # We should ensure the file we are saving has this name or we rename it here.
    # The input image_path might have it, but let's enforce it in the DB storage.
    
    # Actually, Django's save method determines the final filename, 
    # but we can pass a specific name to the save method.
    
    # Generate desired filename
    safe_filename = dish_name_clean.lower().replace(" ", "-") + ".png"
    
    # Read and save
    with open(image_path, 'rb') as f:
        # Save to image field. Django will handle the upload_to path 'menu_items/'
        # We pass the desired filename.
        item.image.save(safe_filename, File(f), save=True)
        
    print(f"✅ Success: Image attached to '{item.name}'")
    print(f"   Stored at: {item.image.name}")
    print(f"   URL: {item.image.url}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python attach_generated_image.py \"<dish_name>\" \"<image_path>\"")
    else:
        name = sys.argv[1]
        path = sys.argv[2]
        attach_image(name, path)
