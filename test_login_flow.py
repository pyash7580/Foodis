#!/usr/bin/env python
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from rest_framework.test import APIClient
from core.models import User, OTP
from datetime import datetime, timedelta

print("=" * 80)
print("TESTING USER LOGIN FLOW")
print("=" * 80)

client = APIClient()

# Get a valid restaurant user
restaurant_user = User.objects.filter(role='RESTAURANT').first()

if not restaurant_user:
    print("[ERROR] No RESTAURANT users found in database!")
    exit(1)

print(f"\nTest User: {restaurant_user.name}")
print(f"Phone: {restaurant_user.phone}")
print(f"Role: {restaurant_user.role}")

# Step 1: Send OTP
print("\n" + "=" * 80)
print("STEP 1: Send OTP")
print("=" * 80)

response = client.post('/api/auth/send-otp/', {
    'phone': restaurant_user.phone,
    'delivery_method': 'sms'
}, format='json')

print(f"\nRequest: POST /api/auth/send-otp/")
print(f"Phone: {restaurant_user.phone}")
print(f"Response Status: {response.status_code}")
print(f"Response: {response.json() if response.status_code < 300 else response.data}")

if response.status_code != 200:
    print("[ERROR] Failed to send OTP!")
    exit(1)

# Get the OTP that was created
otp_obj = OTP.objects.filter(phone=restaurant_user.phone).order_by('-created_at').first()

if otp_obj:
    otp_code = otp_obj.otp_code
    print(f"\n[OK] OTP created: {otp_code}")
else:
    print("[ERROR] OTP not found in database! Using test OTP...")
    otp_code = "000000"  # Test fallback

# Step 2: Verify OTP (Restaurant Login)
print("\n" + "=" * 80)
print("STEP 2: Verify OTP (Restaurant Login)")
print("=" * 80)

response = client.post('/api/auth/verify-otp/', {
    'phone': restaurant_user.phone,
    'otp': otp_code,
    'role': 'RESTAURANT'
}, format='json')

print(f"\nRequest: POST /api/auth/verify-otp/")
print(f"Phone: {restaurant_user.phone}")
print(f"OTP: {otp_code}")
print(f"Role: RESTAURANT")
print(f"Response Status: {response.status_code}")

response_data = response.json() if response.status_code < 300 else response.data
print(f"Response: {json.dumps(response_data, indent=2)}")

# Check for success
if response.status_code == 200 and response_data.get('action') == 'LOGIN':
    print(f"\n[OK] LOGIN SUCCESSFUL!")
    print(f"  - Action: {response_data.get('action')}")
    print(f"  - Message: {response_data.get('message')}")
    if 'token' in response_data:
        print(f"  - Token: {response_data.get('token')[:20]}...")
    if 'user' in response_data:
        print(f"  - User: {response_data['user'].get('name')}")
else:
    print(f"\n[ERROR] Expected LOGIN, got:")
    print(f"  - Status: {response.status_code}")
    print(f"  - Action: {response_data.get('action')}")
    if 'error' in response_data:
        print(f"  - Error: {response_data.get('error')}")

print("\n" + "=" * 80)
print("LOGIN TEST COMPLETE")
print("=" * 80)
