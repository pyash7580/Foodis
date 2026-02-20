import os
import django
import sys

# Setup Django environment
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from django.db import transaction
from django.contrib.auth import get_user_model
from rider_legacy.models import RiderProfile, RiderEarnings, RiderLocation, RiderReview, RiderDocument, RiderBank
from client.models import Order
from collections import Counter

User = get_user_model()

def standardize_phone(phone):
    if not phone:
        return None
    # Remove all non-digits
    digits = ''.join(filter(str.isdigit, str(phone)))
    # Take last 10 digits
    return digits[-10:] if len(digits) >= 10 else digits

def merge_riders():
    print("Starting Rider Identity Standardization & Merging...")
    
    with transaction.atomic():
        all_users = User.objects.all()
        phone_map = {} # standardized_phone -> list of users
        
        for user in all_users:
            if not user.phone:
                continue
                
            std_phone = standardize_phone(user.phone)
            if not std_phone:
                continue
                
            # Update phone to standardized format if it's different and won't cause conflict yet
            if user.phone != std_phone:
                # We can't just save because of UNIQUE constraint if another user has this phone
                # So we collect them first
                pass
                
            if std_phone not in phone_map:
                phone_map[std_phone] = []
            phone_map[std_phone].append(user)
            
        merged_count = 0
        cleaned_count = 0
        
        for std_phone, users in phone_map.items():
            # 1. Update all users to standard format if they are the only one for that phone
            if len(users) == 1:
                user = users[0]
                if user.phone != std_phone:
                    print(f"Standardizing phone for {user.name}: {user.phone} -> {std_phone}")
                    user.phone = std_phone
                    user.save()
                    cleaned_count += 1
                continue
            
            # 2. Merging Logic for duplicates
            print(f"Found {len(users)} duplicates for phone: {std_phone}")
            
            # Sort by: Approved first, then most complete profile, then oldest
            def sort_key(u):
                try:
                    profile = u.rider_profile
                    status_weight = 10 if profile.status == 'APPROVED' else 5 if profile.status == 'PENDING' else 1
                    completeness = profile.onboarding_step
                except:
                    status_weight = 0
                    completeness = 0
                return (status_weight, completeness, -u.id) # Higher weight, then lower ID (older)

            users.sort(key=sort_key, reverse=True)
            primary_user = users[0]
            duplicates = users[1:]
            
            print(f"  Keeping: {primary_user.name} (ID: {primary_user.id}, Phone: {primary_user.phone})")
            
            # Fix primary user phone before deleting others
            primary_user.phone = std_phone
            primary_user.save()
            
            for dupe in duplicates:
                print(f"  Merging & Deleting: {dupe.name} (ID: {dupe.id}, Phone: {dupe.phone})")
                
                # Move related data to primary_user
                RiderEarnings.objects.filter(rider=dupe).update(rider=primary_user)
                RiderLocation.objects.filter(rider=dupe).update(rider=primary_user)
                RiderReview.objects.filter(rider=dupe).update(rider=primary_user)
                RiderReview.objects.filter(user=dupe).update(user=primary_user)
                RiderDocument.objects.filter(rider=dupe).update(rider=primary_user)
                Order.objects.filter(rider=dupe).update(rider=primary_user) # Rider assigned
                Order.objects.filter(user=dupe).update(user=primary_user)   # Client user
                
                # Bank details
                try:
                    dupe_bank = RiderBank.objects.get(rider=dupe)
                    if not RiderBank.objects.filter(rider=primary_user).exists():
                        dupe_bank.rider = primary_user
                        dupe_bank.save()
                    else:
                        dupe_bank.delete() # Primary already has bank
                except RiderBank.DoesNotExist:
                    pass
                
                # Profile details
                try:
                    dupe_profile = RiderProfile.objects.get(rider=dupe)
                    primary_profile, _ = RiderProfile.objects.get_or_create(rider=primary_user)
                    
                    # Merge profile fields if primary is empty
                    if not primary_profile.vehicle_number and dupe_profile.vehicle_number:
                        primary_profile.vehicle_number = dupe_profile.vehicle_number
                    if dupe_profile.is_onboarding_complete:
                        primary_profile.is_onboarding_complete = True
                    if dupe_profile.onboarding_step > primary_profile.onboarding_step:
                        primary_profile.onboarding_step = dupe_profile.onboarding_step
                    
                    primary_profile.save()
                    dupe_profile.delete()
                except RiderProfile.DoesNotExist:
                    pass
                
                # Finally delete the duplicate user
                dupe.delete()
                merged_count += 1

        # 3. Final consistency check: Set is_onboarding_complete for APPROVED riders
        updated_profiles = RiderProfile.objects.filter(status='APPROVED').update(is_onboarding_complete=True)
        
        print(f"\nSummary:")
        print(f"Phones Standardized: {cleaned_count}")
        print(f"Users Merged: {merged_count}")
        print(f"Approved Profiles Ensured Complete: {updated_profiles}")
        print("Done.")

if __name__ == "__main__":
    merge_riders()
