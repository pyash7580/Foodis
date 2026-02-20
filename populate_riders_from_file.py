import os
import django
import sys
import random

# Setup Django Environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from django.contrib.auth import get_user_model
from rider.models import RiderProfile, RiderBank

User = get_user_model()

def populate_riders():
    file_path = 'd:\\Foodis\\RIDER_DETAILS.txt'
    
    if not os.path.exists(file_path):
        print("RIDER_DETAILS.txt not found!")
        return

    print("Reading RIDER_DETAILS.txt...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    count = 0
    updated = 0
    
    for line in lines:
        parts = [p.strip() for p in line.split('|')]
        # Expected format: ID | NAME | EMAIL | PASSWORD | PHONE | VEHICLE | LICENSE | ACCOUNT_HLDR | ACCOUNT_NO | IFSC | BANK | STATUS | CITY
        
        if len(parts) >= 13 and parts[0].isdigit():
            user_id = parts[0]
            name = parts[1]
            email = parts[2]
            password = parts[3]
            phone = parts[4]
            vehicle_no = parts[5]
            license_no = parts[6]
            acc_hldr = parts[7]
            acc_no = parts[8]
            ifsc = parts[9]
            bank_name = parts[10]
            status = parts[11]
            city = parts[12]
            
            # Use phone as primary identifier if available
            # Clean phone
            clean_phone = "".join(filter(str.isdigit, phone))
            if len(clean_phone) > 10:
                clean_phone = clean_phone[-10:]

            if not clean_phone:
                continue

            # Create or Get User
            try:
                user, created = User.objects.get_or_create(
                    phone=clean_phone,
                    defaults={
                        'name': name,
                        'email': email if email and "@" in email else None,
                        'role': 'RIDER',
                        'is_active': True,
                        'is_verified': True
                    }
                )
                
                if created:
                    user.set_password(password)
                    user.save()
                    count += 1
                else:
                    # Update existing user role and email if needed
                    user.role = 'RIDER'
                    if email and "@" in email and not user.email:
                        user.email = email
                    user.save()
                
                # Create or Update Profile
                profile, p_created = RiderProfile.objects.get_or_create(rider=user)
                profile.vehicle_number = vehicle_no if vehicle_no != "N/A" else ""
                profile.license_number = license_no
                profile.status = status if status in dict(RiderProfile.STATUS_CHOICES) else 'APPROVED'
                profile.city = city
                
                if profile.status == 'APPROVED':
                    profile.is_onboarding_complete = True
                    profile.onboarding_step = 6 # Max step
                
                profile.save()

                # Create or Update Bank Details
                bank, b_created = RiderBank.objects.get_or_create(
                    rider=user,
                    defaults={
                        'account_holder_name': acc_hldr or name,
                        'account_number': acc_no,
                        'ifsc_code': ifsc,
                        'bank_name': bank_name,
                        'verified': True
                    }
                )
                
                if not b_created:
                    bank.account_holder_name = acc_hldr or name
                    bank.account_number = acc_no
                    bank.ifsc_code = ifsc
                    bank.bank_name = bank_name
                    bank.verified = True
                    bank.save()
                
                if p_created or created:
                    updated += 1
                    
            except Exception as e:
                print(f"Error processing {name} ({clean_phone}): {e}")

    print(f"\nSUCCESS! Processed {count} new users.")
    print(f"Total Riders Updated/Created: {updated}")


if __name__ == '__main__':
    populate_riders()
