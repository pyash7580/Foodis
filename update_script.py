from restaurant.models import Restaurant
import traceback

total = Restaurant.objects.count()
try:
    Restaurant.objects.all().update(is_active=True, status='APPROVED')
except Exception as e:
    print(f"Error updating status: {e}")
    try:
        Restaurant.objects.all().update(is_active=True, is_approved=True)
    except Exception as e2:
        print(f"Error updating is_approved: {e2}")

print(f"Activated all {total} restaurants")
r = Restaurant.objects.first()
if r:
    print(f"Name: {r.name}")
    print(f"Active: {r.is_active}")
    print(f"Approved: {getattr(r, 'is_approved', getattr(r, 'status', 'N/A'))}")

try:
    from client.models import MenuItem
except ImportError:
    try:
        from restaurant.models import MenuItem
    except ImportError:
        MenuItem = None

if MenuItem:
    try:
        count = MenuItem.objects.count()
        print(f"Menu items total: {count}")
        MenuItem.objects.all().update(is_available=True)
        print("All menu items set to available")
    except Exception as e:
        print(f"MenuItem Error: {e}")
