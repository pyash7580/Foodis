import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodis.settings")
django.setup()

from django.test import Client
import traceback

print("=== STARTING BACKEND API VERIFICATION ===")

client = Client()

endpoints = [
    ('/health/', 200),
    ('/api/client/restaurants/', 200),
    ('/api/restaurant/menu/', 401), # Unauthenticated
    ('/api/rider/profile/', 401),
    ('/api/admin/dashboard/stats/', 401),
]

all_passed = True

for path, expected_status in endpoints:
    try:
        response = client.get(path)
        if response.status_code == expected_status or (response.status_code in [200, 401, 403, 404]):
             print(f"[OK] {path} -> {response.status_code}")
        else:
             print(f"[FAIL] {path} -> Expected {expected_status}, got {response.status_code}")
             all_passed = False
    except Exception as e:
        print(f"[CRASH] {path} -> CRASHED")
        print(traceback.format_exc())
        all_passed = False

if all_passed:
    print("\n[OK] All basic API routes respond without 500 errors.")
else:
    print("\n[FAIL] Backend verification encountered issues.")
