import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from client.models import Restaurant

total = Restaurant.objects.count()
active = Restaurant.objects.filter(is_active=True, status='APPROVED').count()
r = Restaurant.objects.first()

print(f"Total Restaurants: {total}")
print(f"Active & Approved: {active}")
if r:
    print(f"First Restaurant: {r.name}")
    print(f"Image: {r.image}")
    print(f"Image URL: {getattr(r, 'image_url', 'N/A')}")
else:
    print("No restaurants found.")
