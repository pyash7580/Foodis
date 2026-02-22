import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from core.models import User
from client.models import Restaurant
from rider_legacy.models import RiderProfile

roles = ['CLIENT', 'RESTAURANT', 'RIDER', 'ADMIN']
for role in roles:
    user = User.objects.filter(role=role, is_active=True).first()
    if user:
        print(f"{role} User: {user.phone} / {user.email} (ID: {user.id})")
        if role == 'RESTAURANT':
            try:
                rest = Restaurant.objects.get(owner=user)
                print(f"  -> Restaurant: {rest.name} (ID: {rest.id})")
            except:
                 pass
        if role == 'RIDER':
             try:
                 profile = RiderProfile.objects.get(rider=user)
                 print(f"  -> Rider Profile Status: {profile.status}")
             except:
                 pass
    else:
        print(f"No active {role} user found.")
