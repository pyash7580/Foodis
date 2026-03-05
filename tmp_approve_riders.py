import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from core.models import User
from rider_legacy.models import RiderProfile

riders = User.objects.filter(role='RIDER')
print(f"Total riders found: {riders.count()}")

profiles_created = 0
profiles_updated = 0

for rider in riders:
    # Get or create rider profile
    profile, created = RiderProfile.objects.get_or_create(
        rider=rider,
        defaults={
            'status': 'APPROVED',
            'is_onboarding_complete': True,
            'onboarding_step': 6, # Ensure it has the correct step just in case
        }
    )
    
    if created:
        profiles_created += 1
    else:
        # Update existing profile
        profile.status = 'APPROVED'
        profile.is_onboarding_complete = True
        profile.onboarding_step = 6
        profile.save()
        profiles_updated += 1
        
print(f"Profiles created: {profiles_created}")
print(f"Profiles updated: {profiles_updated}")
print("All riders can now log in directly to the dashboard.")
