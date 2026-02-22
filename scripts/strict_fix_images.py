import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from client.models import MenuItem

def fix_menu_item_images():
    base_dir = r"d:\Foodis\media\menu_items"
    
    if not os.path.exists(base_dir):
        print("Menu items directory not found!")
        return

    files = os.listdir(base_dir)
    file_map = {}
    
    for f in files:
        if f.endswith(('png', 'jpg', 'jpeg')):
            clean_name = f.rsplit('.', 1)[0].replace('_', ' ').strip().lower()
            file_map[clean_name] = f
            
    items = MenuItem.objects.all()
    updated = 0
    cleared = 0
    
    for item in items:
        clean_item_name = item.name.lower().strip()
        matched_file = file_map.get(clean_item_name)
        
        # If strict match fails, try without spaces
        if not matched_file:
            target_no_space = clean_item_name.replace(' ', '').replace('-', '')
            for key, filename in file_map.items():
                if key.replace(' ', '').replace('-', '') == target_no_space:
                    matched_file = filename
                    break
                    
        # If still fails, only accept a match if the filename is almost identical 
        # (avoid "Aloo Gobi" matching "Aloo Paratha" just because of "Aloo")
        if not matched_file:
            for key, filename in file_map.items():
                # E.g., if item is "Paneer Tikka Masala" and file is "Paneer Tikka"
                if key in clean_item_name:
                    # Only map if key is significant (more than 1 word, or length > 5)
                    # and the length difference is not huge
                    if len(key) > 5 and abs(len(clean_item_name) - len(key)) <= 10:
                        # Ensure we don't do silly matches like "aloo " in "aloo paratha"
                        if key.split() == clean_item_name.split()[:len(key.split())]:
                            matched_file = filename
                            break
                            
        if matched_file:
            new_path = f"menu_items/{matched_file}"
            if not item.image or item.image.name != new_path:
                item.image = new_path
                item.save()
                updated += 1
        else:
            # If no strict match, MUST CLEAR
            if item.image and item.image.name:
                item.image = None
                item.save()
                cleared += 1
                
    print(f"Strict Matching Done! Updated: {updated}, Cleared: {cleared}")

if __name__ == '__main__':
    fix_menu_item_images()
