import os
import django
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from core.models import City
from client.models import Restaurant, Order
from rider_legacy.models import RiderProfile

def migrate():
    print("Starting city data migration...")
    
    # 1. Create City records
    himmatnagar, _ = City.objects.get_or_create(name='Himmatnagar')
    mehsana, _ = City.objects.get_or_create(name='Mehsana')
    
    cities_map = {
        'Himmatnagar': himmatnagar,
        'Mehsana': mehsana,
        'Himmat Nagar': himmatnagar, # Handle common variations
        'Mehsana ': mehsana,
    }
    
    # 2. Map Restaurants
    print("Migrating Restaurants...")
    for res in Restaurant.objects.all():
        city_name = res.city.strip()
        if city_name in cities_map:
            res.city_id = cities_map[city_name]
            res.save()
            print(f"  Mapped Restaurant '{res.name}' to {res.city_id.name}")
        else:
            print(f"  WARNING: Unknown city '{city_name}' for Restaurant '{res.name}'")

    # 3. Map RiderProfiles
    print("Migrating Riders...")
    for rider in RiderProfile.objects.all():
        city_name = rider.city.strip()
        if city_name in cities_map:
            rider.city_id = cities_map[city_name]
            rider.save()
            print(f"  Mapped Rider '{rider.rider.name}' to {rider.city_id.name}")
        else:
            print(f"  WARNING: Unknown city '{city_name}' for Rider '{rider.rider.name}'")

    # 4. Map Orders
    print("Migrating Orders...")
    for order in Order.objects.all():
        if order.restaurant and order.restaurant.city_id:
            order.city_id = order.restaurant.city_id
            order.save()
            print(f"  Mapped Order {order.order_id} to {order.city_id.name}")
        else:
            print(f"  WARNING: Could not determine city for Order {order.order_id}")

    print("Migration completed successfully!")

if __name__ == "__main__":
    migrate()
