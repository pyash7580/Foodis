import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
os.environ['OPENBLAS_NUM_THREADS'] = '1'
try:
    django.setup()
except Exception as e:
    print(f"Error setting up Django: {e}")
    sys.exit(1)

from client.models import Restaurant, MenuItem

def generate_report():
    print("Generating ALL_DISHES_LIST.txt...")
    
    output_file = 'ALL_DISHES_LIST.txt'
    
    restaurants = Restaurant.objects.all().order_by('name')
    
    total_dishes = MenuItem.objects.count()
    total_restaurants = restaurants.count()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("ALL DISHES - FOODIS PLATFORM\n")
        f.write("=" * 80 + "\n\n\n")
        
        for restaurant in restaurants:
            f.write("=" * 80 + "\n")
            f.write(f"RESTAURANT: {restaurant.name}\n")
            f.write(f"Location: {restaurant.address}, {restaurant.city}\n")
            f.write(f"Total Dishes: {restaurant.menu_items.count()}\n")
            f.write("=" * 80 + "\n\n")
            
            menu_items = restaurant.menu_items.all().order_by('name')
            
            if not menu_items:
                f.write("   [NO DISHES AVAILABLE]\n\n")
                continue
                
            for idx, item in enumerate(menu_items, 1):
                veg_tag = "[VEG]" if item.veg_type == 'VEG' else "[NON-VEG]"
                cat_name = item.category.name if item.category else "N/A"
                
                f.write(f"{idx}. {item.name}\n")
                f.write(f"   Type: {veg_tag} {item.veg_type}\n")
                f.write(f"   Price: Rs. {item.price}\n")
                f.write(f"   Category: {cat_name}\n")
                f.write(f"   Status: {'Available' if item.is_available else 'Not Available'}\n")
                f.write(f"   Description: {item.description}\n\n")
            
            f.write("\n")
            
        f.write("=" * 80 + "\n")
        f.write("SUMMARY\n")
        f.write("=" * 80 + "\n")
        f.write(f"Total Restaurants: {total_restaurants}\n")
        f.write(f"Total Dishes: {total_dishes}\n")
        f.write("=" * 80 + "\n")

    print(f"Report generated: {output_file}")
    print(f"Stats: {total_restaurants} restaurants, {total_dishes} dishes")

if __name__ == '__main__':
    generate_report()
