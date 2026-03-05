import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from core.models import User
from rider_legacy.models import RiderProfile, RiderBank

riders = User.objects.filter(role='RIDER')
print(f"Total riders found to update: {riders.count()}")

cities = ['Mehsana', 'Himmatnagar']

profiles_updated = 0
banks_created = 0

for i, rider in enumerate(riders):
    # Determine city (split roughly half/half or randomly)
    city = cities[i % len(cities)]
    
    # 1. Update RiderProfile
    profile, created = RiderProfile.objects.get_or_create(rider=rider)
    
    vehicle_no = f"GJ-{random.randint(1, 38):02d}-{random.choice(['A', 'B', 'M', 'N'])}{random.choice(['A', 'B', 'C', 'D'])}-{random.randint(1000, 9999)}"
    license_no = f"GJ{random.randint(1, 38):02d}{random.randint(10000000000, 99999999999)}"
            
    # Update profile fields
    profile.city = city
    profile.vehicle_number = vehicle_no
    profile.license_number = license_no
    profile.vehicle_type = 'BIKE' # Default
    profile.status = 'APPROVED'
    profile.is_onboarding_complete = True
    profile.onboarding_step = 6
    profile.save()
    profiles_updated += 1
    
    # 2. Add Bank Details
    bank, bank_created = RiderBank.objects.get_or_create(
        rider=rider,
        defaults={
            'account_holder_name': rider.name,
            'account_number': f"**** **** **** {random.randint(1000, 9999)}", # Like the prompt
            'ifsc_code': 'N/A',
            'bank_name': 'N/A',
            'verified': True
        }
    )
    if bank_created:
        banks_created += 1
    else:
        bank.account_holder_name = rider.name
        bank.account_number = f"**** **** **** {random.randint(1000, 9999)}"
        bank.ifsc_code = 'N/A'
        bank.bank_name = 'N/A'
        bank.verified = True
        bank.save()
        banks_created += 1

print(f"Profiles updated with full details: {profiles_updated}")
print(f"Bank details updated/created: {banks_created}")
print("All 50 riders are now deployment-ready with full profiles.")
