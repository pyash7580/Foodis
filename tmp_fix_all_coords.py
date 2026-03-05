import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from rider_legacy.models import RiderProfile
from core.models import City

riders = RiderProfile.objects.all()
updated = 0

for profile in riders:
    city_name = None
    if profile.city_id:
        city_name = profile.city_id.name
    elif profile.city:
        city_name = profile.city.strip()
        
        # apply normalization
        if city_name == 'Mehsana ': city_name = 'Mehsana'
        if city_name == 'Himmat Nagar': city_name = 'Himmatnagar'

    if city_name and hasattr(profile, 'CITY_CENTERS') and city_name in profile.CITY_CENTERS:
        center = profile.CITY_CENTERS[city_name]
        profile.current_latitude = center['lat']
        profile.current_longitude = center['lng']
        profile.save()
        updated += 1

print(f"Updated coordinates for {updated} rider profiles to match their cities.")
