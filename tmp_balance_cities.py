import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodis.settings")
django.setup()

from core.models import User
from rider.models import Rider
from rider_legacy.models import RiderProfile

def balance_cities():
    riders = list(User.objects.filter(role='RIDER').order_by('id'))
    total = len(riders)
    mid = total // 2
    
    print(f"Total Riders: {total}")
    
    for i, user in enumerate(riders):
        city = 'Mehsana' if i < mid else 'Himmatnagar'
        
        # 1. Update Core User (if it has city)
        if hasattr(user, 'city'):
            user.city = city
            user.save()
            
        # 2. Update Rider model
        try:
            rider = Rider.objects.get(email=user.email)
            rider.city = city
            rider.save()
        except Rider.DoesNotExist:
            pass
            
        # 3. Update Legacy RiderProfile
        try:
            profile = RiderProfile.objects.get(rider=user)
            profile.city = city
            profile.save()
        except RiderProfile.DoesNotExist:
            pass
            
    print(f"Assigned {mid} to Mehsana and {total - mid} to Himmatnagar.")

if __name__ == '__main__':
    balance_cities()
