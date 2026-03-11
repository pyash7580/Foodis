"""
Email Service Module for Foodis

Handles OTP generation, sending, and verification via email.
Uses SendGrid HTTP API v3 (port 443) to avoid SMTP port blocking on Railway/cloud.
Falls back to Django send_mail() for local dev when no API key is set.
"""

import random
import string
import logging
import requests
import os
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from core.models import OTP
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

logger = logging.getLogger(__name__)


def generate_otp(length=6):
    """Generate a random OTP of specified length"""
    return ''.join(random.choices(string.digits, k=length))


def send_email_otp(email, purpose='LOGIN'):
    """
    Generate and send OTP to email address via Brevo HTTP API.
    """
    try:
        # Validate email
        if not email or '@' not in email:
            logger.error(f"Invalid email format: {email}")
            return None
        
        # Clean up any previous unused OTPs for this email
        OTP.objects.filter(
            email=email,
            is_used=False,
            is_verified=False
        ).delete()
        
        # Generate OTP
        otp_code = generate_otp(length=settings.OTP_LENGTH)
        
        # Calculate expiry
        expiry_minutes = settings.OTP_EXPIRY_MINUTES
        expires_at = timezone.now() + timedelta(minutes=expiry_minutes)
        
        # Save OTP to database
        otp_record = OTP.objects.create(
            email=email,
            otp_code=otp_code,
            purpose=purpose,
            expires_at=expires_at
        )
        
        # Send via Brevo HTTP API
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = getattr(settings, 'BREVO_API_KEY', '')
        
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )
        
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": email}],
            sender={"name": "Foodis", "email": getattr(settings, 'BREVO_FROM_EMAIL', 'mryash7580@gmail.com')},
            subject="Foodis - Email Verification Code",
            html_content=f"""
                <div style='font-family:Arial,sans-serif;max-width:400px;margin:auto;padding:20px;'>
                    <h2 style='color:#e53935;'>Foodis Verification</h2>
                    <p>Your OTP verification code is:</p>
                    <h1 style='letter-spacing:8px;color:#333;background:#f5f5f5;
                               padding:15px;text-align:center;border-radius:8px;'>
                        {otp_code}
                    </h1>
                    <p>This code expires in <strong>{expiry_minutes} minutes</strong>.</p>
                    <p style='color:#999;font-size:12px;'>
                        Do not share this with anyone.
                    </p>
                </div>
            """
        )
        
        api_instance.send_transac_email(send_smtp_email)
        logger.info(f"[EMAIL_OTP_SENT] Email: {email} | OTP: {otp_code} | Expires: {expires_at}")
        
        # Dev mode: Log OTP to console
        if settings.DEBUG:
            print(f"\n{'='*60}")
            print(f"[DEV MODE] OTP EMAIL SENT")
            print(f"To: {email}")
            print(f"Code: {otp_code}")
            print(f"Expires in: {expiry_minutes} minutes")
            print(f"{'='*60}\n")
        
        return otp_code
        
    except Exception as e:
        logger.error(f"[EMAIL_OTP_ERROR] Failed to send OTP to {email}: {str(e)}", exc_info=True)
        return None


def verify_email_otp(email, otp_code):
    """
    Verify OTP for email address.
    
    Args:
        email (str): Email address to verify
        otp_code (str): OTP code to verify
    
    Returns:
        bool: True if OTP is valid, False otherwise
    """
    try:
        # Convert OTP to string for comparison
        otp_code = str(otp_code).strip()
        
        if not email or not otp_code:
            logger.warning(f"[OTP_VERIFY] Missing email or OTP code")
            return False
        
        # Query OTP record
        otp_record = OTP.objects.filter(
            email=email,
            otp_code=otp_code,
            is_used=False
        ).first()
        
        if not otp_record:
            logger.warning(f"[OTP_VERIFY] No OTP found for {email}")
            return False
        
        # Check if expired
        if otp_record.is_expired():
            logger.warning(f"[OTP_VERIFY] OTP expired for {email}")
            otp_record.is_used = True
            otp_record.save()
            return False
        
        # Check attempt count
        max_attempts = settings.OTP_ATTEMPTS_LIMIT
        if otp_record.attempt_count >= max_attempts:
            logger.warning(f"[OTP_VERIFY] Too many attempts for {email}")
            otp_record.is_used = True
            otp_record.save()
            return False
        
        # Verify OTP
        if otp_record.otp_code == otp_code:
            otp_record.is_verified = True
            otp_record.is_used = True
            otp_record.save()
            logger.info(f"[OTP_VERIFIED] Email: {email}")
            return True
        else:
            otp_record.attempt_count += 1
            otp_record.save()
            logger.warning(f"[OTP_INVALID] Email: {email} | Attempt: {otp_record.attempt_count}")
            return False
            
    except Exception as e:
        logger.error(f"[OTP_VERIFY_ERROR] {email}: {str(e)}", exc_info=True)
        return False


def get_otp_status(email):
    """
    Get OTP status for debugging/monitoring.
    
    Returns:
        dict: Status information
    """
    try:
        otp_record = OTP.objects.filter(email=email).order_by('-created_at').first()
        if not otp_record:
            return {'status': 'NOT_FOUND'}
        
        return {
            'status': 'EXISTS',
            'email': otp_record.email,
            'is_verified': otp_record.is_verified,
            'is_used': otp_record.is_used,
            'is_expired': otp_record.is_expired(),
            'attempts': otp_record.attempt_count,
            'created_at': otp_record.created_at,
            'expires_at': otp_record.expires_at,
        }
    except Exception as e:
        logger.error(f"[OTP_STATUS_ERROR] {email}: {str(e)}")
        return {'status': 'ERROR', 'error': str(e)}
