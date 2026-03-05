#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from core.models import User
from rider_legacy.models import RiderProfile
from rider.models import Rider

print("=" * 60)
print("INITIALIZING RIDER PROFILES")
print("=" * 60)

# Get all riders
all_riders = User.objects.filter(role='RIDER')
total_riders = all_riders.count()

print(f"\n✓ Total riders: {total_riders}")

missing_count = 0
created_count = 0
updated_count = 0

for idx, user in enumerate(all_riders, 1):
    has_profile = hasattr(user, 'rider_profile')
    
    if not has_profile:
        missing_count += 1
        # Create missing RiderProfile
        profile = RiderProfile.objects.create(
            rider=user,
            city='Mehsana',
            status='APPROVED',
            is_online=False,
            vehicle_type='BIKE',
            vehicle_number=f'MH-{idx:03d}',
            mobile_number=f'9999{idx:06d}',
            rating=4.5,
        )
        created_count += 1
        print(f"  ✓ {idx}. Created profile for {user.name} ({user.email})")
    else:
        profile = user.rider_profile
        # Check if profile has all required fields
        updated = False
        
        if not profile.mobile_number:
            profile.mobile_number = f'9999{idx:06d}'
            updated = True
            
        if not profile.vehicle_number:
            profile.vehicle_number = f'MH-{idx:03d}'
            updated = True
            
        if not profile.vehicle_type:
            profile.vehicle_type = 'BIKE'
            updated = True
            
        if profile.status == 'NEW':
            profile.status = 'APPROVED'
            updated = True
            
        if updated:
            profile.save()
            updated_count += 1
            print(f"  ✓ {idx}. Updated profile for {user.name}")

print("\n" + "=" * 60)
print(f"✓ Created profiles: {created_count}")
print(f"✓ Updated profiles: {updated_count}")
print(f"✓ Riders with complete profiles: {total_riders}")
print("=" * 60)
print("✓ All riders initialized successfully!")
print("=" * 60)
