#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from core.models import User
from rider.models import Rider
from rider_legacy.models import RiderProfile
from django.contrib.auth.hashers import make_password

# Delete existing user if it exists
User.objects.filter(email='rakesh.kumar@foodis.com').delete()
Rider.objects.filter(email='rakesh.kumar@foodis.com').delete()

# Create user in core.User for authentication
user = User.objects.create_user(
    email='rakesh.kumar@foodis.com',
    password='Rakesh@',
    name='Rakesh Kumar',
    role='RIDER',
    is_active=True,
    is_verified=True,
    email_verified=True
)

# Create rider profile
rider = Rider.objects.create(
    email='rakesh.kumar@foodis.com',
    password=make_password('Rakesh@'),
    full_name='Rakesh Kumar',
    city='Delhi',
    is_active=True,
    is_online=False,
    wallet_balance=0.0,
)

# Create RiderProfile for legacy compatibility
rider_profile = RiderProfile.objects.create(
    rider=user,
    city='Delhi',
    status='APPROVED',
    is_online=False,
    wallet_balance=0.0,
)

print(f"✓ Created user: {user.email}")
print(f"✓ Created rider profile: {rider.full_name}")
print(f"✓ Created RiderProfile: {rider_profile.id}")
print(f"Email: {rider.email}")
print(f"Password: Rakesh@")
