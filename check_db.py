import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()
from client.models import Restaurant, Category
from core.models import OTP

print(f"RESTAURANTS: {Restaurant.objects.count()}")
print(f"CATEGORIES: {Category.objects.count()}")
print(f"LATEST_OTPS: {OTP.objects.count()}")

if Restaurant.objects.exists():
    r = Restaurant.objects.first()
    print(f"FIRST_REST: {r.name} | STATUS: {r.status} | ACTIVE: {r.is_active}")
else:
    print("NO_RESTAURANTS_FOUND")
