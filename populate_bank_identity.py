#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from core.models import User
from rider_legacy.models import RiderBank, RiderProfile

print("=" * 60)
print("POPULATING RIDER BANK & IDENTITY DETAILS")
print("=" * 60)

# Get all riders
all_riders = User.objects.filter(role='RIDER')
total_riders = all_riders.count()

print(f"\n✓ Total riders: {total_riders}")

bank_created = 0
profile_updated = 0

for idx, user in enumerate(all_riders, 1):
    # Add Bank Details if missing
    if not hasattr(user, 'rider_bank'):
        bank = RiderBank.objects.create(
            rider=user,
            account_holder_name=user.name,
            account_number=f'4000{idx:06d}',  # Sample account number
            ifsc_code='SBIN0001234',
            bank_name='State Bank of India',
            verified=False,
        )
        bank_created += 1
        print(f"  ✓ {idx}. Created bank account for {user.name}")
    
    # Add Identity details if missing
    if hasattr(user, 'rider_profile'):
        profile = user.rider_profile
        updated = False
        
        if not profile.aadhar_number:
            profile.aadhar_number = f'{12 * idx:012d}'[:12]  # Sample aadhar
            updated = True
            
        if not profile.pan_number:
            profile.pan_number = f'PAN{idx:08d}'.replace('PAN0', 'AAAA')[:10]  # Sample PAN
            updated = True
            
        if updated:
            profile.save()
            profile_updated += 1
            print(f"  ✓ {idx}. Updated identity for {user.name}")

print("\n" + "=" * 60)
print(f"✓ Created bank accounts: {bank_created}")
print(f"✓ Updated identity details: {profile_updated}")
print(f"✓ Total riders with complete data: {total_riders}")
print("=" * 60)
print("✓ Bank & Identity details populated successfully!")
print("=" * 60)
