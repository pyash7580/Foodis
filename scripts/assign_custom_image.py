import sys
import os
import django
import argparse
from django.core.files import File

# Setup Django environment
# Assumes script is in <project_root>/scripts/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from client.models import MenuItem

def normalize_name(name):
    """Normalize string by removing extra whitespace and converting to lowercase."""
    if not name:
        return ""
    return ' '.join(name.split()).lower()

def assign_image(dish_name, image_path, overwrite=False):
    stats = {
        "updated": 0,
        "skipped": 0,
        "warnings": [],
        "errors": []
    }

    print(f"Processing Request: Dish='{dish_name}' | Image='{image_path}'")

    # 1. Validate Image Path
    if not os.path.exists(image_path):
        error_msg = f"Image file not found: {image_path}"
        stats["errors"].append(error_msg)
        print(f"ERROR: {error_msg}")
        return stats

    if not os.path.isfile(image_path):
        error_msg = f"Path is not a file: {image_path}"
        stats["errors"].append(error_msg)
        print(f"ERROR: {error_msg}")
        return stats

    # 2. Normalize Target Name
    target_normalized = normalize_name(dish_name)
    if not target_normalized:
         stats["errors"].append("Dish name cannot be empty")
         return stats

    # 3. Find Matches
    # We iterate all to ensure robust matching (ignoring extra spaces inside/outside)
    # Optimization: Filter by first word to reduce set if needed, but for <10k items, full scan is fast.
    
    # We can try a broad filter first to speed up
    first_word = target_normalized.split()[0] if target_normalized else ""
    if len(first_word) > 2:
        candidates = MenuItem.objects.filter(name__icontains=first_word)
    else:
        candidates = MenuItem.objects.all()

    matching_dishes = []
    for dish in candidates:
        if normalize_name(dish.name) == target_normalized:
            matching_dishes.append(dish)

    # 4. Handle Not Found
    if not matching_dishes:
        warning_msg = f"Dish Not Found – {dish_name}"
        stats["warnings"].append(warning_msg)
        print(f"WARNING: {warning_msg}")
        return stats

    print(f"Found {len(matching_dishes)} matching dish(es).")

    # 5. Apply Image
    for dish in matching_dishes:
        try:
            # Check existing
            if dish.image and not overwrite:
                stats["skipped"] += 1
                stats["warnings"].append(f"Skipped '{dish.name}' (ID: {dish.id}) - Image exists. Use --overwrite to force.")
                continue

            # Save Image
            # We open the file fresh for each save to ensure pointer is at start/valid
            with open(image_path, 'rb') as f:
                filename = os.path.basename(image_path)
                # Save to updated location. 
                # Note: This copies the file into the media/menu_items/ folder managed by Django
                dish.image.save(filename, File(f), save=True)
                stats["updated"] += 1
                print(f"Updated '{dish.name}' (ID: {dish.id})")

        except Exception as e:
            error_msg = f"Failed to save image for '{dish.name}': {str(e)}"
            stats["errors"].append(error_msg)
            print(f"ERROR: {error_msg}")

    return stats

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Attach provided image to matching dishes.")
    parser.add_argument("name", help="Dish Name")
    parser.add_argument("image", help="Image File Path")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing images if present")
    
    args = parser.parse_args()
    
    result = assign_image(args.name, args.image, args.overwrite)
    
    print("\n" + "="*30)
    print("      EXECUTION REPORT      ")
    print("="*30)
    print(f"Updated: {result['updated']} dishes")
    print(f"Skipped: {result['skipped']} dishes")
    
    if result['warnings']:
        print("\nWarnings:")
        for w in result['warnings']:
            print(f"- {w}")
            
    if result['errors']:
        print("\nErrors:")
        for e in result['errors']:
            print(f"- {e}")
    print("="*30)
