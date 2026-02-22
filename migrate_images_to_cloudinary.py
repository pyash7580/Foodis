import os
import sys
import django
import cloudinary.uploader

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodis.settings")
django.setup()

from client.models import Restaurant, MenuItem

def migrate_images():
    print("Starting migration of Restaurant images...")
    for restaurant in Restaurant.objects.all():
        if restaurant.image and 'cloudinary' not in str(restaurant.image):
            try:
                # Check if file exists locally before uploading
                if os.path.exists(restaurant.image.path):
                    result = cloudinary.uploader.upload(
                        restaurant.image.path,
                        folder='foodis/restaurants'
                    )
                    restaurant.image = result['public_id']
                    restaurant.save()
                    print(f"Migrated image for: {restaurant.name}")
                else:
                    print(f"Local file missing for {restaurant.name}: {restaurant.image}")
            except Exception as e:
                print(f"Failed image migration for {restaurant.name}: {e}")
        
        if restaurant.cover_image and 'cloudinary' not in str(restaurant.cover_image):
            try:
                if os.path.exists(restaurant.cover_image.path):
                    result = cloudinary.uploader.upload(
                        restaurant.cover_image.path,
                        folder='foodis/restaurants/covers'
                    )
                    restaurant.cover_image = result['public_id']
                    restaurant.save()
                    print(f"Migrated cover image for: {restaurant.name}")
                else:
                    print(f"Local cover file missing for {restaurant.name}: {restaurant.cover_image}")
            except Exception as e:
                print(f"Failed cover image migration for {restaurant.name}: {e}")

    print("\nStarting migration of MenuItem images...")
    for item in MenuItem.objects.all():
        if item.image and 'cloudinary' not in str(item.image):
            try:
                if os.path.exists(item.image.path):
                    result = cloudinary.uploader.upload(
                        item.image.path,
                        folder='foodis/menu_items'
                    )
                    item.image = result['public_id']
                    item.save()
                    print(f"Migrated dish image: {item.name}")
                else:
                    print(f"Local file missing for dish {item.name}: {item.image}")
            except Exception as e:
                print(f"Failed dish image migration for {item.name}: {e}")

if __name__ == "__main__":
    migrate_images()
