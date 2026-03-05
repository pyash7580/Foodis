import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from rider_legacy.models import RiderProfile

rakesh = RiderProfile.objects.get(rider_id=503)
rakesh.city = 'Mehsana'
rakesh.save()
print("Rakesh Kumar's city updated to Mehsana!")
