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
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from core.models import OTP

logger = logging.getLogger(__name__)


def generate_otp(length=6):
    """Generate a random OTP of specified length"""
    return ''.join(random.choices(string.digits, k=length))


def send_email_otp(email, purpose='LOGIN'):
    """
    Generate and send OTP to email address via SendGrid.
    
    Args:
        email (str): Email address to send OTP to
        purpose (str): Purpose of OTP (LOGIN, REGISTER, PIN_RESET)
    
    Returns:
        str: Generated OTP code on success, None on failure
    
    Raises:
        Exception: If email sending fails (logged, not fatal)
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
        
        # Prepare email content
        subject = f'Foodis Verification Code: {otp_code}'
        
        # Email template context
        context = {
            'otp_code': otp_code,
            'expiry_minutes': expiry_minutes,
            'purpose': purpose,
            'company_name': 'Foodis',
        }
        
        # Simple HTML email (can be enhanced with template)
        html_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h2 style="color: #333; text-align: center;">Foodis Verification</h2>
                    <p style="color: #666; font-size: 16px;">Hi there,</p>
                    <p style="color: #666; font-size: 16px;">Your verification code is:</p>
                    
                    <div style="background-color: #f0f0f0; padding: 20px; text-align: center; margin: 20px 0; border-radius: 8px;">
                        <h1 style="color: #FF6B35; letter-spacing: 5px; margin: 0;">{otp_code}</h1>
                    </div>
                    
                    <p style="color: #999; font-size: 14px;">This code expires in {expiry_minutes} minutes.</p>
                    <p style="color: #999; font-size: 14px;">Please do not share this code with anyone. Foodis staff will never ask for this code.</p>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    
                    <p style="color: #999; font-size: 12px; text-align: center;">
                        © 2026 Foodis. All rights reserved.
                    </p>
                </div>
            </body>
        </html>
        """
        
        plain_message = f"Your Foodis verification code is: {otp_code}\n\nThis code expires in {expiry_minutes} minutes."
        
        # Use SendGrid HTTP API if API key is available (bypasses SMTP port blocking)
        api_key = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
        from_email = settings.EMAIL_FROM
        
        if api_key:
            # SendGrid v3 Mail Send API — uses HTTPS port 443, never blocked
            resp = requests.post(
                'https://api.sendgrid.com/v3/mail/send',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json',
                },
                json={
                    'personalizations': [{'to': [{'email': email}]}],
                    'from': {'email': from_email},
                    'subject': subject,
                    'content': [
                        {'type': 'text/plain', 'value': plain_message},
                        {'type': 'text/html', 'value': html_message},
                    ],
                },
                timeout=15,
            )
            if resp.status_code not in (200, 201, 202):
                logger.error(f"[SENDGRID_HTTP_ERROR] {resp.status_code}: {resp.text}")
                raise Exception(f"SendGrid API error {resp.status_code}: {resp.text}")
        else:
            # Local dev — use Django email backend (ConsoleEmailBackend)
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=from_email,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )
        
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
