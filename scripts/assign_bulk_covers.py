
import os
import sys
import django
import random

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from client.models import Restaurant
from django.conf import settings

def assign_bulk_covers():
    # 1. Get all images in the covers directory
    covers_dir = os.path.join(settings.MEDIA_ROOT, 'restaurants', 'covers')
    if not os.path.exists(covers_dir):
        print(f"Error: Directory not found: {covers_dir}")
        return

    all_files = [f for f in os.listdir(covers_dir) if os.path.isfile(os.path.join(covers_dir, f))]
    valid_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    images = [f for f in all_files if os.path.splitext(f)[1].lower() in valid_extensions]
    
    print(f"Found {len(images)} images in {covers_dir}")

    # 2. Get all restaurants
    restaurants = list(Restaurant.objects.all())
    print(f"Found {len(restaurants)} restaurants.")

    # 3. Strategy: 
    #    a. Try to match by name (e.g. "Saffron Lounge" -> "saffron_lounge_cover.png")
    #    b. Assign remaining images to remaining restaurants
    
    assigned_images = set()
    restaurants_to_assign = []

    # Helper to normalize names for matching
    def normalize(name):
        return name.lower().replace(' ', '_').replace("'", "")

    # Pass 1: Name Matching
    for r in restaurants:
        r_name_norm = normalize(r.name)
        match = None
        
        # Try finding a file that starts with the restaurant name
        for img in images:
            if img in assigned_images:
                continue
            
            img_name_norm = normalize(os.path.splitext(img)[0])
            # Check for exact match or "name_cover" match
            if img_name_norm == r_name_norm or img_name_norm == f"{r_name_norm}_cover":
                match = img
                break
        
        if match:
            # Assign
            relative_path = f"restaurants/covers/{match}"
            r.cover_image.name = relative_path
            r.save()
            assigned_images.add(match)
            print(f"MATCHED: {r.name} -> {match}")
        else:
            restaurants_to_assign.append(r)

    # Pass 2: Assign remaining unique images
    available_images = [img for img in images if img not in assigned_images]
    
    # Shuffle for randomness
    random.shuffle(available_images)
    
    print(f"\nAssigning remaining {len(restaurants_to_assign)} restaurants from {len(available_images)} available images...")

    for i, r in enumerate(restaurants_to_assign):
        if not available_images:
            print("Warning: Ran out of unique images! Recycling images...")
            # Reload all images to recycle if needed (though user asked not to repeat, if we have to, we have to)
            available_images = images.copy()
            random.shuffle(available_images)

        image = available_images.pop(0)
        relative_path = f"restaurants/covers/{image}"
        r.cover_image.name = relative_path
        r.save()
        print(f"ASSIGNED: {r.name} -> {image}")

    print("\nBulk update complete.")

if __name__ == "__main__":
    assign_bulk_covers()
