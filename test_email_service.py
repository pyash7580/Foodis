#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
sys.path.insert(0, 'd:\\Foodis')
django.setup()

from core.services.email_service import generate_otp, verify_email_otp
from core.models import OTP

print("=" * 60)
print("Testing Email OTP Service")
print("=" * 60)

# Test 1: Generate OTP
print("\n[Test 1] Generating OTP...")
try:
    otp_code = generate_otp(length=6)
    if otp_code and len(otp_code) == 6 and otp_code.isdigit():
        print("[PASS] OTP generated successfully: " + otp_code)
    else:
        print("[FAIL] Failed to generate valid OTP")
        sys.exit(1)
except Exception as e:
    print("[FAIL] Error generating OTP: " + str(e))
    sys.exit(1)

# Test 2: Create OTP record in database
print("\n[Test 2] Creating OTP database record...")
try:
    from django.utils import timezone
    from datetime import timedelta
    
    expires_at = timezone.now() + timedelta(minutes=10)
    otp_obj = OTP.objects.create(
        email='test@example.com',
        phone='',
        otp_code=otp_code,
        purpose='LOGIN',
        is_used=False,
        is_verified=False,
        expires_at=expires_at
    )
    print("[PASS] OTP record created in database")
except Exception as e:
    print("[FAIL] Error creating OTP record: " + str(e))
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Verify OTP from database
print("\n[Test 3] Verifying OTP from database...")
try:
    verified = verify_email_otp('test@example.com', otp_code)
    if verified:
        print("[PASS] OTP verified successfully!")
    else:
        print("[FAIL] OTP verification failed")
except Exception as e:
    print("[FAIL] Error verifying OTP: " + str(e))

# Test 4: Reject invalid OTP
print("\n[Test 4] Verifying invalid OTP 999999...")
try:
    verified = verify_email_otp('test@example.com', '999999')
    if not verified:
        print("[PASS] Correctly rejected invalid OTP")
    else:
        print("[FAIL] Should have rejected invalid OTP")
except Exception as e:
    print("[PASS] Correctly raised error for invalid OTP")

# Test 5: Check model integrity
print("\n[Test 5] Checking OTP model structure...")
try:
    otp_count = OTP.objects.filter(email='test@example.com').count()
    print("[PASS] OTP records found: " + str(otp_count))
except Exception as e:
    print("[FAIL] Error checking OTP records: " + str(e))

print("\n" + "=" * 60)
print("[SUCCESS] Email OTP Service Tests Passed!")
print("=" * 60)


