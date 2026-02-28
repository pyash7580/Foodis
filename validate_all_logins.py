
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def log(msg):
    print(f"\n[TEST] {msg}")

def test_flow(name, endpoint, payload, expected_status=200):
    url = f"{BASE_URL}{endpoint}"
    log(f"Testing {name}...")
    try:
        response = requests.post(url, json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code == expected_status:
            print(f"[OK] {name} PASSED")
            return response.json()
        else:
            print(f"[FAIL] {name} FAILED: {response.text}")
            return None
    except Exception as e:
        print(f"[CRASH] {name} CRASHED: {e}")
        return None

def run_all_tests():
    success = True

    # 1. CLIENT FLOW
    client_email = "mryash7580@gmail.com"
    send_res = test_flow("Client Send OTP", "/api/auth/send-otp/", {"email": client_email})
    if not send_res: success = False
    
    otp = send_res.get('otp') if send_res else None
    if otp:
        verify_res = test_flow("Client Verify OTP", "/api/auth/verify-otp/", {
            "email": client_email,
            "otp_code": otp,
            "role": "CLIENT"
        })
        if not verify_res: success = False
    else:
        log("Skipping verify (no OTP returned in debug)")
        success = False

    # 2. RESTAURANT FLOW (PASSWORD)
    res_login = test_flow("Restaurant Login (Password)", "/api/auth/login/", {
        "email": "test_restaurant@example.com",
        "password": "password123"
    })
    if not res_login: success = False

    # 3. RIDER FLOW (PASSWORD)
    rider_login = test_flow("Rider Login (Password)", "/api/auth/login/", {
        "email": "test_rider@example.com",
        "password": "password123"
    })
    if not rider_login: success = False

    # 4. ADMIN FLOW (OTP)
    admin_email = "admin@foodis.com"
    admin_send = test_flow("Admin Send OTP", "/api/auth/send-otp/", {"email": admin_email})
    if not admin_send: success = False
    
    admin_otp = admin_send.get('otp') if admin_send else None
    if admin_otp:
        admin_verify = test_flow("Admin Verify OTP", "/api/auth/verify-otp/", {
            "email": admin_email,
            "otp_code": admin_otp,
            "role": "ADMIN"
        })
        if not admin_verify: success = False

    if success:
        log("OVERALL RESULT: ALL LOGIN FLOWS PERFECT!")
        sys.exit(0)
    else:
        log("OVERALL RESULT: SOME TESTS FAILED")
        sys.exit(1)

if __name__ == "__main__":
    run_all_tests()
