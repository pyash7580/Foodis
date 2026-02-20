
import requests
import json
import os
import django
import sys

# Setup Django for DB checks
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from core.models import User, OTP
from django.utils import timezone
from datetime import timedelta

BASE_URL = 'http://localhost:8000'

def verify_auth_logic():
    print("\n--- Verifying Authentication Logic Fix ---")

    test_phone = "9000000001"
    
    # Ensure user does NOT exist
    User.objects.filter(phone=test_phone).delete()
    print(f"1. Testing NEW number: {test_phone}")

    # Send OTP
    print(f"   -> Sending OTP...")
    send_res = requests.post(f"{BASE_URL}/api/auth/send-otp/", json={"phone": test_phone})
    otp_code = send_res.json().get('otp')
    print(f"   -> OTP Received: {otp_code}")

    # Verify OTP
    print(f"   -> Verifying OTP as NEW user...")
    verify_res = requests.post(f"{BASE_URL}/api/auth/verify-otp/", json={"phone": test_phone, "otp_code": otp_code})
    data = verify_res.json()
    
    print(f"   -> Response Data: {json.dumps(data, indent=2)}")
    
    if data.get('action') == 'REGISTER' and 'token' not in data:
        print("PASS: New number triggers REGISTER and no token is issued.")
    else:
        print("FAIL: Unexpected response for new user.")

    # Now Register the user
    print(f"\n2. Registering NEW user: {test_phone}")
    reg_res = requests.post(f"{BASE_URL}/api/auth/register/", json={
        "phone": test_phone,
        "name": "Test User",
        "email": "test@example.com",
        "role": "CLIENT"
    })
    reg_data = reg_res.json()
    print(f"   -> Registration response: {json.dumps(reg_data, indent=2)}")
    
    if reg_res.status_code == 201 and reg_data.get('token'):
        print("PASS: Registration successful and token issued.")
    else:
        print("FAIL: Registration failed.")

    # Now test LOGIN (Existing user)
    print(f"\n3. Testing EXISTING number: {test_phone}")
    
    # Send OTP again
    send_res = requests.post(f"{BASE_URL}/api/auth/send-otp/", json={"phone": test_phone})
    otp_code = send_res.json().get('otp')
    
    # Verify OTP
    print(f"   -> Verifying OTP as EXISTING user...")
    verify_res = requests.post(f"{BASE_URL}/api/auth/verify-otp/", json={"phone": test_phone, "otp_code": otp_code})
    data = verify_res.json()
    
    print(f"   -> Response Data: {json.dumps(data, indent=2)}")
    
    if data.get('action') == 'LOGIN' and data.get('token'):
        print("PASS: Existing user triggers LOGIN and token is issued.")
    else:
        print("FAIL: Unexpected response for existing user.")

    # Cleanup
    User.objects.filter(phone=test_phone).delete()
    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    verify_auth_logic()
