import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodis.settings")
django.setup()

import logging
logging.disable(logging.CRITICAL)

import traceback

print("=== TESTING DATABASE ===")
try:
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("SELECT 1")
    print("✅ Database connection OK")
except Exception as e:
    print("❌ DATABASE CONNECTION FAILED:")
    print(traceback.format_exc())

print("\n=== TESTING USER MODEL ===")
try:
    from core.models import User
    count = User.objects.count()
    print(f"✅ Users in DB: {count}")
except Exception as e:
    print("❌ USER MODEL ERROR:")
    print(traceback.format_exc())

print("\n=== TESTING RESTAURANT MODEL ===")
try:
    from restaurant.models import Restaurant
    count = Restaurant.objects.count()
    print(f"✅ Total Restaurants: {count}")
    active = Restaurant.objects.filter(
        is_active=True, status='APPROVED'
    ).count()
    print(f"✅ Active+Approved: {active}")
    if active < 48:
        Restaurant.objects.all().update(
            is_active=True, status='APPROVED'
        )
        print("✅ Fixed: all restaurants set to active+approved")
except Exception as e:
    print("❌ RESTAURANT MODEL ERROR:")
    print(traceback.format_exc())

print("\n=== TESTING PROFILE SERIALIZER ===")
try:
    from core.models import User
    from core.serializers import UserSerializer
    user = User.objects.first()
    if user:
        data = UserSerializer(user).data
        print(f"✅ UserSerializer OK: {list(data.keys())}")
    else:
        print("⚠️ No users in database")
except Exception as e:
    print("❌ USER SERIALIZER ERROR:")
    print(traceback.format_exc())

print("\n=== TESTING RESTAURANT SERIALIZER ===")
try:
    from restaurant.models import Restaurant
    from client.serializers import RestaurantSerializer
    rest = Restaurant.objects.first()
    if rest:
        data = RestaurantSerializer(rest).data
        print(f"✅ RestaurantSerializer OK: {list(data.keys())}")
    else:
        print("⚠️ No restaurants in database")
except Exception as e:
    print("❌ RESTAURANT SERIALIZER ERROR:")
    print(traceback.format_exc())
