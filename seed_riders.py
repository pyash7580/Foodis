import os
import django
import sys
import random
import re

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from django.contrib.auth import get_user_model
from rider_legacy.models import RiderProfile, RiderBank
from rider.models import Rider as TemplateRider

User = get_user_model()

FILE_PATH = r'd:\Foodis\RIDER_DETAILS.txt'

def parse_line(line):
    # Split by '|' and strip whitespace
    parts = [p.strip() for p in line.split('|')]
    if len(parts) < 12:
        return None
    
    return {
        'id': parts[0],
        'name': parts[1],
        'email': parts[2],
        'password': parts[3],
        'phone': parts[4],
        'vehicle': parts[5],
        'license': parts[6],
        'acc_name': parts[7],
        'acc_no': parts[8],
        'ifsc': parts[9],
        'bank_name': parts[10],
        'status': parts[11],
        'city': parts[12] if len(parts) > 12 else ''
    }

def seed_riders():
    print("Starting Rider Seeding (220 Partners)...")
    
    if not os.path.exists(FILE_PATH):
        print(f"Error: {FILE_PATH} not found!")
        return

    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    count = 0
    updated = 0

    for line in lines:
        if line.startswith('=') or line.startswith('ID') or not line.strip() or '|' not in line:
            continue
            
        data = parse_line(line)
        if not data:
            continue

        # Clean phone (remove spaces, ensure 10 digits)
        raw_phone = re.sub(r'\D', '', data['phone'])
        if len(raw_phone) > 10:
            phone = raw_phone[-10:]
        elif len(raw_phone) == 10:
            phone = raw_phone
        else:
            print(f"Skipping invalid phone: {data['phone']}")
            continue

        # 1. Create/Update User (Core Auth)
        try:
            user, created = User.objects.get_or_create(
                phone=phone,
                defaults={
                    'name': data['name'],
                    'email': data['email'] or f"rider{phone}@example.com",
                    'role': 'RIDER',
                    'is_active': True,
                    'is_verified': True
                }
            )
            
            # Sync password if provided
            if data['password']:
                user.set_password(data['password'])
                user.save()
            elif created:
                user.set_password('password123')
                user.save()

            if created:
                count += 1
            else:
                updated += 1

            # 2. Create/Update Profile (rider_legacy)
            profile, _ = RiderProfile.objects.get_or_create(rider=user)
            profile.vehicle_number = data['vehicle'] if data['vehicle'] != 'N/A' else f"GJ-01-XX-{random.randint(1000,9999)}"
            profile.vehicle_type = 'BIKE'
            profile.city = data['city']
            profile.mobile_number = phone
            profile.status = 'APPROVED'
            profile.license_number = data['license']
            profile.is_onboarding_complete = True
            profile.save()

            # 3. Create/Update Bank (rider_legacy)
            bank, _ = RiderBank.objects.get_or_create(rider=user)
            bank.account_holder_name = data['acc_name']
            bank.account_number = data['acc_no']
            bank.ifsc_code = data['ifsc']
            bank.bank_name = data['bank_name']
            bank.verified = True
            bank.save()

            # 4. Create/Update Template Rider (rider app)
            template_rider, _ = TemplateRider.objects.get_or_create(
                phone=phone,
                defaults={'full_name': data['name']}
            )
            template_rider.full_name = data['name']
            template_rider.is_active = True
            template_rider.save()

            print(f"Processed: {user.name} ({phone})")

        except Exception as e:
            print(f"Error processing {data['name']}: {e}")

    print(f"\nSeeding Complete!")
    print(f"Created: {count}")
    print(f"Updated: {updated}")

if __name__ == '__main__':
    seed_riders()
