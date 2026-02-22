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
    
    # Create a mapping of simplified name to filename
    for f in files:
        if f.endswith(('png', 'jpg', 'jpeg')):
            # E.g. "Aloo Gobi.png" -> "aloo gobi"
            clean_name = f.rsplit('.', 1)[0].replace('_', ' ').lower()
            file_map[clean_name] = f
            
    items = MenuItem.objects.all()
    updated = 0
    cleared = 0
    
    for item in items:
        clean_item_name = item.name.lower()
        
        # Try to find an exact or very close match
        matched_file = file_map.get(clean_item_name)
        
        if not matched_file:
            # Fallback heuristic: Try to find if the filename is inside the item name or vice versa
            for key, filename in file_map.items():
                if key in clean_item_name or clean_item_name in key:
                    matched_file = filename
                    break
        
        if matched_file:
            new_path = f"menu_items/{matched_file}"
            if item.image.name != new_path:
                item.image.name = new_path
                item.save()
                updated += 1
                print(f"✅ Matched: {item.name} -> {new_path}")
        else:
            if item.image:
                print(f"❌ Cleared: {item.name} (had {item.image.name})")
                item.image = None
                item.save()
                cleared += 1
                
    print(f"Done! Updated: {updated}, Cleared: {cleared}")

if __name__ == '__main__':
    fix_menu_item_images()
