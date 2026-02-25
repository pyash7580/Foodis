import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from django.contrib.auth import get_user_model
from rider_legacy.models import RiderProfile, RiderBank
from rider.models import Rider

User = get_user_model()

def sync_riders():
    print("Starting Rider Sync...")
    rider_users = User.objects.filter(role='RIDER', is_active=True)
    count = 0
    updated = 0

    for user in rider_users:
        # Check if they have a new Rider model entry
        rider, _ = Rider.objects.get_or_create(
            phone=user.phone,
            defaults={
                'full_name': user.name,
                'city': 'Ahmedabad',
                'is_active': True,
                'status': 'ONLINE',
                'is_online': True,
                'wallet_balance': Decimal(0)
            }
        )

        # Create/Update legacy Profile
        profile, created = RiderProfile.objects.get_or_create(rider=user)
        
        # Only populate if it's newly created or empty
        if created or not profile.vehicle_number:
            profile.vehicle_number = f"GJ-01-RD-{user.id:04d}"
            profile.vehicle_type = 'BIKE'
            profile.city = rider.city or 'Ahmedabad'
            profile.mobile_number = user.phone
            profile.status = 'APPROVED'
            profile.license_number = f"GJ01 {user.id:010d}"
            profile.is_onboarding_complete = True
            profile.save()

        # Create/Update legacy Bank
        bank, b_created = RiderBank.objects.get_or_create(rider=user)
        if b_created or not bank.account_number:
            bank.account_holder_name = user.name
            bank.account_number = f"1000{user.id:010d}"
            bank.ifsc_code = "HDFC0001234"
            bank.bank_name = "HDFC Bank"
            bank.verified = True
            bank.save()

        if created or b_created:
            count += 1
        else:
            updated += 1
            
    print(f"Sync complete. New profiles: {count}, Existing verified: {updated}")
    print(f"Total RiderProfiles: {RiderProfile.objects.count()}")

if __name__ == '__main__':
    sync_riders()
