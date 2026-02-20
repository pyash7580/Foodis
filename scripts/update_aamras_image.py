import os
import sys
import django
from django.core.files import File
from django.conf import settings

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from client.models import MenuItem

def update_aamras_image(image_path):
    try:
        # Find the dish
        dish = MenuItem.objects.get(name="Aamras (Seasonal)")
        print(f"Found dish: {dish.name} (ID: {dish.id})")
        
        # Check if file exists
        if not os.path.exists(image_path):
            print(f"Error: Image file not found at {image_path}")
            return
            
        # Open and update image
        with open(image_path, 'rb') as f:
            dish.image.save(os.path.basename(image_path), File(f), save=True)
            
        print(f"Successfully updated image for {dish.name}")
        print(f"New image URL: {dish.image.url}")
        
    except MenuItem.DoesNotExist:
        print("Error: Dish 'Aamras (Seasonal)' not found in database.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/update_aamras_image.py <path_to_image>")
    else:
        update_aamras_image(sys.argv[1])
