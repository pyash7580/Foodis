
import os
import sys
import django
import argparse
from django.core.files import File

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from client.models import Restaurant

def update_restaurant_cover(restaurant_name, image_path):
    try:
        if not os.path.exists(image_path):
            print(f"Error: Image file not found at {image_path}")
            return False

        restaurant = Restaurant.objects.filter(name__icontains=restaurant_name).first()
        if not restaurant:
            print(f"Error: Restaurant '{restaurant_name}' not found.")
            return False

        print(f"Updating cover image for: {restaurant.name} (ID: {restaurant.id})")
        
        with open(image_path, 'rb') as f:
            # Save properly handles media root
            filename = os.path.basename(image_path)
            restaurant.cover_image.save(filename, File(f), save=True)
            
        print(f"Successfully updated cover image for {restaurant.name}")
        print(f"New Image Path: {restaurant.cover_image.url}")
        return True

    except Exception as e:
        print(f"Error updating cover image: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update restaurant cover image")
    parser.add_argument("name", help="Restaurant Name (partial match)")
    parser.add_argument("image_path", help="Absolute path to the new image file")
    
    args = parser.parse_args()
    
    update_restaurant_cover(args.name, args.image_path)
