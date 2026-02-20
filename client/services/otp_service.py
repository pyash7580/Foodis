import hashlib
import random
import uuid
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
from rest_framework.exceptions import ValidationError
from datetime import timedelta
from client.models import Order, OrderOTP

class OTPService:
    """
    Service for handling Secure Order OTP Generation, Hashing, and Verification.
    Uses DB for secure hashed storage and Cache for temporary plaintext display.
    """

    CACHE_TIMEOUT_PICKUP = 300  # 5 Minutes
    CACHE_TIMEOUT_DELIVERY = 600 # 10 Minutes

    @staticmethod
    def _hash_otp(otp_plain: str) -> str:
        """Helper to hash OTP using SHA256."""
        return hashlib.sha256(otp_plain.encode()).hexdigest()

    @staticmethod
    def _get_cache_key(order_id, otp_type):
        return f"otp_{order_id}_{otp_type}"

    @staticmethod
    def generate_otp(order: Order, otp_type: str, related_user=None) -> str:
        """
        Generates a new secure OTP for a specific order and type.
        Invalidates any existing active OTPs for the same order & type.
        Returns the plaintext OTP.
        """
        # 1. Validation Logic
        if otp_type == 'PICKUP':
            # Allow READY, ACCEPTED, WAITING_FOR_RIDER
            pass 
        elif otp_type == 'DELIVERY':
            # Allow PICKED_UP, ON_THE_WAY
            pass 

        # 2. Invalidate existing DB records
        OrderOTP.objects.filter(
            order=order,
            otp_type=otp_type,
            is_used=False
        ).update(expires_at=timezone.now())

        # 3. Generate
        otp_plain = f"{random.randint(100000, 999999)}"
        otp_hash = OTPService._hash_otp(otp_plain)

        # 4. Determine Expiry
        expiry_minutes = 5 if otp_type == 'PICKUP' else 10
        expires_at = timezone.now() + timedelta(minutes=expiry_minutes)
        cache_timeout = OTPService.CACHE_TIMEOUT_PICKUP if otp_type == 'PICKUP' else OTPService.CACHE_TIMEOUT_DELIVERY

        # 5. Store in DB (Hash only)
        OrderOTP.objects.create(
            order=order,
            otp_hash=otp_hash,
            otp_type=otp_type,
            related_user=related_user,
            expires_at=expires_at,
            is_used=False,
            attempt_count=0
        )

        # 6. Store in Cache (Plaintext for display)
        cache_key = OTPService._get_cache_key(order.order_id, otp_type)
        cache.set(cache_key, otp_plain, timeout=cache_timeout)

        return otp_plain

    @staticmethod
    def get_valid_otp(order: Order, otp_type: str) -> str:
        """
        Retrieves the valid plaintext OTP from cache.
        Returns None if expired/missing (requires regeneration).
        """
        cache_key = OTPService._get_cache_key(order.order_id, otp_type)
        otp_plain = cache.get(cache_key)
        
        if otp_plain:
            return otp_plain
            
        # Optional: Failover - Check if DB has valid record? 
        # No, we cannot recover plaintext from hash. 
        # User MUST regenerate.
        return None

    @staticmethod
    def verify_otp(order: Order, otp_type: str, input_otp: str, user=None) -> bool:
        """
        Verifies the provided OTP for the order against DB hash.
        """
        try:
            # Fetch active OTPs
            active_otps = OrderOTP.objects.filter(
                order=order,
                otp_type=otp_type,
                is_used=False,
                expires_at__gt=timezone.now()
            ).order_by('-created_at')

            if not active_otps.exists():
                raise ValidationError(f"{otp_type} OTP expired or not generated.")

            otp_record = active_otps.first()

            # Check Attempts
            if otp_record.attempt_count >= 5:
                otp_record.expires_at = timezone.now()
                otp_record.save()
                raise ValidationError("Max OTP attempts reached. Please regenerate.")

            # Validate Hash
            input_hash = OTPService._hash_otp(str(input_otp).strip())
            
            if otp_record.otp_hash == input_hash:
                otp_record.is_used = True
                otp_record.verified_at = timezone.now()
                otp_record.related_user = user
                otp_record.save()
                
                # Clear Cache
                cache_key = OTPService._get_cache_key(order.order_id, otp_type)
                cache.delete(cache_key)
                
                return True
            else:
                otp_record.attempt_count += 1
                otp_record.save()
                raise ValidationError("Invalid OTP. Please try again.")

        except OrderOTP.DoesNotExist:
            raise ValidationError("No active OTP found.")
            
