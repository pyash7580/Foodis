#!/usr/bin/env python3
import requests
import json

BACKEND_URL = "https://happy-purpose-production.up.railway.app"

# Test data
phone = "+919999999991"
otp_code = "123456"

print("=" * 80)
print("FOODIS OTP VERIFICATION DIAGNOSIS")
print("=" * 80)

# Step 1: Send OTP
print("\n[STEP 1] Sending OTP...")
resp = requests.post(
    f"{BACKEND_URL}/api/auth/send-otp/",
    json={"phone": phone, "role": "CLIENT"},
    timeout=10
)
print(f"Status: {resp.status_code}")
print(f"Response: {json.dumps(resp.json(), indent=2)}")

send_data = resp.json()
returned_otp = send_data.get("otp")
print(f"\nOTP returned from send: {returned_otp}")

# Step 2: Verify OTP - try different formats
verify_payloads = [
    {"phone": phone, "otp_code": otp_code, "role": "CLIENT"},
    {"phone": "9999999991", "otp_code": otp_code, "role": "CLIENT"},
    {"phone": phone, "otp_code": returned_otp if returned_otp else "123456"},
]

for i, payload in enumerate(verify_payloads, 1):
    print(f"\n[STEP 2.{i}] Verifying OTP with payload: {payload}")
    resp = requests.post(
        f"{BACKEND_URL}/api/auth/verify-otp/",
        json=payload,
        timeout=10
    )
    print(f"Status: {resp.status_code}")
    try:
        print(f"Response: {json.dumps(resp.json(), indent=2)}")
    except:
        print(f"Response: {resp.text}")
