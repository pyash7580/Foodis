import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from rider_legacy.models import RiderProfile
from core.models import City

rakesh = RiderProfile.objects.get(rider_id=503)

print("Before:")
print(f"City: {rakesh.city}")
print(f"City ID: {rakesh.city_id.name if rakesh.city_id else None}")
print(f"Coords: {rakesh.current_latitude}, {rakesh.current_longitude}")

mehsana_city = City.objects.filter(name__iexact='Mehsana').first()

rakesh.city = 'Mehsana'
rakesh.city_id = mehsana_city
if hasattr(rakesh, 'CITY_CENTERS'):
    center = rakesh.CITY_CENTERS.get('Mehsana')
    if center:
        # Force the coordinates directly just in case save() messes it up
        rakesh.current_latitude = center['lat']
        rakesh.current_longitude = center['lng']

rakesh.save()

print("\nAfter:")
print(f"City: {rakesh.city}")
print(f"City ID: {rakesh.city_id.name if rakesh.city_id else None}")
print(f"Coords: {rakesh.current_latitude}, {rakesh.current_longitude}")
