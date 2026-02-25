import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()
from rider.models import Rider
from client.models import Restaurant
from core.models import User
print(f'FINAL_COUNTS | RIDERS:{Rider.objects.count()} | RESTAURANTS:{Restaurant.objects.count()} | USERS:{User.objects.count()}')
