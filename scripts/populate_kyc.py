import os
import sys
import django
import random

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from rider_legacy.models import RiderProfile

def populate_kyc_data():
    print("Populating missing KYC data for riders...")
    
    riders = RiderProfile.objects.all()
    updated_count = 0
    
    for profile in riders:
        changed = False
        
        # Generate Aadhar (12 digits)
        if not profile.aadhar_number:
            profile.aadhar_number = f"{random.randint(2000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}"
            changed = True
            
        # Generate PAN (ABCDE1234F)
        if not profile.pan_number:
            chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            nums = "0123456789"
            pan = "".join(random.choices(chars, k=5)) + \
                  "".join(random.choices(nums, k=4)) + \
                  random.choice(chars)
            profile.pan_number = pan
            changed = True
            
        if changed:
            profile.save()
            updated_count += 1
            
    print(f"Successfully updated KYC data for {updated_count} riders.")

if __name__ == "__main__":
    populate_kyc_data()
