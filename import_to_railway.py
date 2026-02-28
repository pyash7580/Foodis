"""
Import data to Railway PostgreSQL database
This script should be uploaded to Railway and run there
"""
import os
import sys

def import_data():
    """Import data to Railway database"""
    print("📥 Importing data to Railway database...")
    
    # Check if we have the data file
    if not os.path.exists('railway_data.json'):
        print("❌ Error: railway_data.json not found!")
        print("Please upload railway_data.json to Railway first.")
        sys.exit(1)
    
    import django
    import json
    
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
    django.setup()
    
    from core.models import User
    from client.models import Restaurant, MenuItem, Order
    from rider.models import Rider
    from django.db import transaction
    
    # Read JSON
    with open('railway_data.json', 'r') as f:
        data = json.load(f)
    
    print(f"Found data:")
    print(f"   - Users: {len(data['users'])}")
    print(f"   - Restaurants: {len(data['restaurants'])}")
    print(f"   - Menu Items: {len(data['menu_items'])}")
    print(f"   - Orders: {len(data['orders'])}")
    print(f"   - Riders: {len(data['riders'])}")
    print("\nImporting...")
    
    with transaction.atomic():
        # Import Users
        print("Importing users...")
        for user_data in data['users']:
            User.objects.update_or_create(
                id=user_data['id'],
                defaults=user_data
            )
        
        # Import Restaurants
        print("Importing restaurants...")
        for rest_data in data['restaurants']:
            Restaurant.objects.update_or_create(
                id=rest_data['id'],
                defaults=rest_data
            )
        
        # Import Menu Items
        print("Importing menu items...")
        for item_data in data['menu_items']:
            MenuItem.objects.update_or_create(
                id=item_data['id'],
                defaults=item_data
            )
        
        # Import Orders
        print("Importing orders...")
        for order_data in data['orders']:
            Order.objects.update_or_create(
                id=order_data['id'],
                defaults=order_data
            )
        
        # Import Riders
        print("Importing riders...")
        for rider_data in data['riders']:
            Rider.objects.update_or_create(
                id=rider_data['id'],
                defaults=rider_data
            )
    
    print(f"\n✅ Import Complete!")

if __name__ == '__main__':
    import_data()
