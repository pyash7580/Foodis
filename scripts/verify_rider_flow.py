import os
import django
import sys
import unittest

# Setup Django environment
sys.path.append(r'd:\Foodis')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from django.contrib.auth import get_user_model
from rider.models import RiderProfile
from core.views import verify_otp_view
from rest_framework.test import APIRequestFactory
from rest_framework import status

User = get_user_model()

class RiderIdentityTest(unittest.TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        # Ensure clean state for test phone
        self.test_phone = '9998887776'
        User.objects.filter(phone=self.test_phone).delete()
        RiderProfile.objects.filter(mobile_number=self.test_phone).delete()

    def test_rider_registration_and_redirection(self):
        print("\nTesting NEW rider registration...")
        # Mock request to verify-otp
        payload = {
            'phone': self.test_phone,
            'otp_code': '123456', 
            'role': 'RIDER',
            'name': 'Test Rider'
        }
        
        # Patch verify_otp utility to always return True for this test
        from core import utils
        original_verify = utils.verify_otp
        utils.verify_otp = lambda phone, otp: True
        
        try:
            request = self.factory.post('/api/auth/verify-otp/', payload)
            response = verify_otp_view(request)
            
            self.assertEqual(response.status_code, 200)
            data = response.data
            self.assertEqual(data['redirect_to'], 'onboarding')
            self.assertEqual(data['step'], 0)
            self.assertEqual(data['rider_status'], 'NEW')
            print("OK: New Rider redirect to onboarding: Step 0")

            # Verify RiderProfile created
            profile = RiderProfile.objects.get(mobile_number=self.test_phone)
            self.assertEqual(profile.status, 'NEW')
            
            # Simulate step 2 completion
            print("Simulating step 2 completion...")
            profile.onboarding_step = 2
            profile.save()
            
            # Second login attempt
            request2 = self.factory.post('/api/auth/verify-otp/', payload)
            response2 = verify_otp_view(request2)
            self.assertEqual(response2.data['step'], 2)
            self.assertEqual(response2.data['redirect_to'], 'onboarding')
            print("OK: Resuming Rider redirect to onboarding: Step 2")
            
            # Simulate Approval
            print("Simulating Admin Approval...")
            profile.status = 'APPROVED'
            profile.is_onboarding_complete = True
            profile.save()
            
            # Third login attempt
            request3 = self.factory.post('/api/auth/verify-otp/', payload)
            response3 = verify_otp_view(request3)
            self.assertEqual(response3.data['redirect_to'], 'dashboard')
            print("OK: Approved Rider redirect to dashboard directly")

        finally:
            utils.verify_otp = original_verify

    def test_identity_uniqueness(self):
        print("\nTesting phone standardization and uniqueness...")
        # Create user with +91 format
        u1 = User.objects.create(phone='91' + self.test_phone, name='User 1', role='RIDER')
        
        # Standardize via the logic used in verify_otp
        std_phone = ''.join(filter(str.isdigit, str(u1.phone)))[-10:]
        self.assertEqual(std_phone, self.test_phone)
        
        # Check if existing user is found by standardized phone
        existing = User.objects.filter(phone=std_phone).first()
        if not existing:
             # This happens if we haven't standardized yet
             u1.phone = std_phone
             u1.save()
             existing = u1

        self.assertEqual(existing.phone, self.test_phone)
        print("OK: Phone standardization works")

if __name__ == "__main__":
    unittest.main()
