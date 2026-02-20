import os
import django
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from client.models import Order
from rider_legacy.models import RiderProfile

def debug_city_mismatch():
    print("=== City Mismatch Debug Tool ===")
    
    # Check Orders without city_id
    null_city_orders = Order.objects.filter(city_id__isnull=True)
    if null_city_orders.exists():
        print(f"ERROR: Found {null_city_orders.count()} orders with NO city_id:")
        for o in null_city_orders:
            print(f"  - Order {o.order_id} (Restaurant: {o.restaurant.name}, City: {o.restaurant.city})")
    else:
        print("SUCCESS: All orders have a city_id.")

    # Check RiderProfiles without city_id
    null_city_riders = RiderProfile.objects.filter(city_id__isnull=True)
    if null_city_riders.exists():
        print(f"ERROR: Found {null_city_riders.count()} riders with NO city_id:")
        for r in null_city_riders:
            print(f"  - Rider {r.rider.name} ({r.mobile_number}, City: {r.city})")
    else:
        print("SUCCESS: All riders have a city_id.")

    # Highlight Mismatches (e.g. Order in Himmatnagar but Restaurant says Mehsana - though we copy it, let's verify)
    mismatched_orders = []
    for o in Order.objects.filter(city_id__isnull=False):
        if o.city_id != o.restaurant.city_id:
            mismatched_orders.append(o)
    
    if mismatched_orders:
        print(f"ERROR: Found {len(mismatched_orders)} orders with city mismatch vs Restaurant:")
        for o in mismatched_orders:
            print(f"  - Order {o.order_id} (City: {o.city_id.name}, Restaurant City: {o.restaurant.city_id.name})")
    else:
        print("SUCCESS: No order/restaurant city mismatches found.")

    print("\n=== Visibility Check ===")
    online_riders = RiderProfile.objects.filter(is_online=True, city_id__isnull=False)
    available_orders = Order.objects.filter(status__in=['CONFIRMED', 'PREPARING', 'READY'], rider__isnull=True, city_id__isnull=False)
    
    for rider in online_riders:
        matching_orders = available_orders.filter(city_id=rider.city_id)
        other_orders = available_orders.exclude(city_id=rider.city_id)
        print(f"Rider {rider.rider.name} (City: {rider.city_id.name} | Online: {rider.is_online})")
        print(f"  - Can see: {matching_orders.count()} matching orders")
        if other_orders.exists():
            print(f"  - Cannot see: {other_orders.count()} orders from other cities")

if __name__ == "__main__":
    debug_city_mismatch()
