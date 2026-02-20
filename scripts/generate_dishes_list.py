import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from client.models import MenuItem, Restaurant

def generate_dishes_report():
    """Generate a text file with all dishes grouped by restaurant"""
    
    output_file = 'ALL_DISHES_LIST.txt'
    
    # Get all restaurants with their menu items
    restaurants = Restaurant.objects.prefetch_related('menu_items').filter(status='APPROVED').order_by('name')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("ALL DISHES - FOODIS PLATFORM\n")
        f.write("=" * 80 + "\n\n")
        
        total_restaurants = 0
        total_dishes = 0
        
        for restaurant in restaurants:
            dishes = restaurant.menu_items.all().order_by('name')
            
            if dishes.exists():
                total_restaurants += 1
                f.write(f"\n{'='*80}\n")
                f.write(f"RESTAURANT: {restaurant.name}\n")
                f.write(f"Location: {restaurant.address}\n")
                f.write(f"Total Dishes: {dishes.count()}\n")
                f.write(f"{'='*80}\n\n")
                
                for idx, dish in enumerate(dishes, 1):
                    total_dishes += 1
                    veg_symbol = "[VEG]" if dish.veg_type == 'VEG' else "[NON-VEG]" if dish.veg_type == 'NON_VEG' else "[EGG]"
                    availability = "Available" if dish.is_available else "Unavailable"
                    
                    f.write(f"{idx}. {dish.name}\n")
                    f.write(f"   Type: {veg_symbol} {dish.veg_type}\n")
                    f.write(f"   Price: ₹{dish.price}\n")
                    f.write(f"   Category: {dish.category.name if dish.category else 'N/A'}\n")
                    f.write(f"   Status: {availability}\n")
                    if dish.description:
                        f.write(f"   Description: {dish.description[:100]}...\n")
                    f.write("\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write(f"SUMMARY\n")
        f.write(f"=" * 80 + "\n")
        f.write(f"Total Restaurants: {total_restaurants}\n")
        f.write(f"Total Dishes: {total_dishes}\n")
        f.write(f"=" * 80 + "\n")
    
    print("Report generated successfully!")
    print(f"File saved as: {output_file}")
    print(f"Total Restaurants: {total_restaurants}")
    print(f"Total Dishes: {total_dishes}")

if __name__ == '__main__':
    generate_dishes_report()
