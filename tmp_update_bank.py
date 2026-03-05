import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from core.models import User
from rider_legacy.models import RiderBank

riders = User.objects.filter(role='RIDER')

banks = ['HDFC Bank', 'ICICI Bank', 'State Bank of India', 'Axis Bank', 'Kotak Mahindra Bank']

updated = 0
for rider in riders:
    try:
        bank = RiderBank.objects.get(rider=rider)
        bank_name = random.choice(banks)
        
        # Generate IFSC like HDFC0001234
        bank_prefix = bank_name.split()[0].upper()[:4].ljust(4, 'X')
        ifsc = f"{bank_prefix}000{random.randint(1000, 9999)}"
        
        bank.bank_name = bank_name
        bank.ifsc_code = ifsc
        bank.save()
        updated += 1
    except RiderBank.DoesNotExist:
        pass

print(f"Updated {updated} rider bank details with realistic dummy data.")
