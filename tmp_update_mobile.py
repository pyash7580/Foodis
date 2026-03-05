import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from core.models import User
from rider_legacy.models import RiderProfile

riders = User.objects.filter(role='RIDER')
print(f"Total riders found: {riders.count()}")

profiles_updated = 0

for rider in riders:
    profile, created = RiderProfile.objects.get_or_create(rider=rider)
    
    # Generate realistic mobile number if empty
    if not profile.mobile_number:
        # Avoid collisions
        while True:
            mobile = f"9{random.randint(100000000, 999999999)}"
            if not RiderProfile.objects.filter(mobile_number=mobile).exists():
                profile.mobile_number = mobile
                break
        
        profile.save(update_fields=['mobile_number'])
        profiles_updated += 1

print(f"Assigned mobile numbers to {profiles_updated} profiles.")
