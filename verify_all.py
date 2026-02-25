import os
import django
import requests
import json
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from client.models import Restaurant, Category, MenuItem
from core.models import User, OTP

BASE_URL = "https://happy-purpose-production.up.railway.app"

def test_api():
    print("--- [A] INFRASTRUCTURE CHECK ---")
    try:
        r = requests.get(f"{BASE_URL}/health/", timeout=10)
        print(f"Healthcheck: {r.status_code}")
    except Exception as e:
        print(f"Healthcheck FAILED: {e}")

    print("\n--- [B] PUBLIC DATA CHECK ---")
    print(f"DB Restaurants: {Restaurant.objects.count()}")
    print(f"DB Categories: {Category.objects.count()}")
    print(f"DB Menu Items: {MenuItem.objects.count()}")
    
    try:
        r = requests.get(f"{BASE_URL}/api/client/restaurants/", timeout=10)
        data = r.json()
        print(f"API Restaurants Found: {len(data)}")
    except Exception as e:
        print(f"API Restaurants FAILED: {e}")

    print("\n--- [C] AUTH FLOW CHECK ---")
    phone = "9824949865"
    try:
        # 1. Send OTP
        r = requests.post(f"{BASE_URL}/api/auth/send-otp/", json={"phone": phone}, timeout=10)
        send_data = r.json()
        otp = send_data.get('otp')
        print(f"OTP Sent: {otp}")
        
        if otp:
            # 2. Verify OTP
            r = requests.post(f"{BASE_URL}/api/auth/verify-otp/", json={"phone": phone, "otp_code": otp}, timeout=10)
            verify_data = r.json()
            token = verify_data.get('token')
            print(f"OTP Verified: {'SUCCESS' if token else 'FAILED'}")
            
            if token:
                # 3. Profile Access
                headers = {"Authorization": f"Bearer {token}"}
                r = requests.get(f"{BASE_URL}/api/auth/profile/", headers=headers, timeout=10)
                print(f"Profile Access: {r.status_code}")
                if r.status_code == 200:
                    print(f"Profile User: {r.json().get('phone')}")
    except Exception as e:
        print(f"Auth Flow FAILED: {e}")

if __name__ == "__main__":
    test_api()
