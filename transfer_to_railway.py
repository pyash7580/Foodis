"""
Transfer local SQLite data to Railway PostgreSQL database
"""
import os
import django
import json
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from django.core import serializers
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from core.models import User
from client.models import Restaurant, MenuItem, Order
from rider.models import Rider

def export_data():
    """Export data from local SQLite"""
    print("📤 Exporting data from local database...")
    
    data = {
        'users': list(User.objects.all().values()),
        'restaurants': list(Restaurant.objects.all().values()),
        'menu_items': list(MenuItem.objects.all().values()),
        'orders': list(Order.objects.all().values()),
        'riders': list(Rider.objects.all().values()),
    }
    
    # Save to JSON
    with open('railway_data.json', 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"✅ Exported:")
    print(f"   - Users: {len(data['users'])}")
    print(f"   - Restaurants: {len(data['restaurants'])}")
    print(f"   - Menu Items: {len(data['menu_items'])}")
    print(f"   - Orders: {len(data['orders'])}")
    print(f"   - Riders: {len(data['riders'])}")
    print(f"\n📁 Data saved to: railway_data.json")

if __name__ == '__main__':
    export_data()
