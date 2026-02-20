import random
import string
import logging
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
import requests
from .models import OTP

logger = logging.getLogger(__name__)


def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))


def clean_phone(phone):
    """Standardize phone to 10 digits, handling various formats"""
    if phone is None:
        return ""
    # Remove all non-digits
    digits = ''.join(filter(str.isdigit, str(phone)))
    # Return last 10 digits if longer (handling +91 prefix)
    return digits[-10:] if len(digits) >= 10 else digits


def send_otp_sms(phone, otp):
    """Send OTP via MSG91 SMS service"""
    try:
        # MSG91 API endpoint
        url = "https://control.msg91.com/api/v5/otp"
        
        # Get API key from settings
        api_key = getattr(settings, 'MSG91_API_KEY', None)
        template_id = getattr(settings, 'MSG91_TEMPLATE_ID', None)
        
        if not api_key:
            # Fallback: log to console/debug if no API key configured
            logger.info(f"OTP for {phone}: {otp}")
            if settings.DEBUG:
                print(f"OTP for {phone}: {otp}")
            return True
        
        # MSG91 payload
        payload = {
            "template_id": template_id,
            "mobile": phone.replace('+91', ''),  # Remove country code
            "otp": otp
        }
        
        headers = {
            "authkey": api_key,
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # FAILSAFE: Log in DEBUG mode
            if settings.DEBUG:
                logger.debug(f"[CRITICAL DEBUG] OTP FOR {phone}: {otp}")
                
            return True
        else:
            logger.error(f"Failed to send OTP to {phone}: {response.text}")
            # Fallback to logging
            logger.warning(f"FALLBACK OTP FOR {phone}: {otp}")
            if settings.DEBUG:
                print(f"FALLBACK OTP FOR {phone}: {otp}")
            return True
            
    except Exception as e:
        # print(f"❌ Error sending OTP: {str(e)}")
        # Fallback: print to console
        # print(f"\n{'='*50}")
        # print(f"📱 FALLBACK OTP for {phone}: {otp}")
        # print(f"{'='*50}\n")
        return True


def send_otp(phone):
    """Generate and send OTP to phone number"""
    phone = clean_phone(phone)
    otp_code = generate_otp()
    
    # Log OTP generation
    logger.info(f"OTP GENERATED | PHONE: {phone} | CODE: {otp_code}")
    if settings.DEBUG:
        print(f"OTP GENERATED | PHONE: {phone} | CODE: {otp_code}")
    
    # Store in DB (more reliable than cache for dev)
    expiry_minutes = getattr(settings, 'OTP_EXPIRY_MINUTES', 5)
    expires_at = timezone.now() + timezone.timedelta(minutes=expiry_minutes)
    
    # NEW LOGIC: Invalidate previous active OTPs
    OTP.objects.filter(phone=phone, is_used=False).update(is_verified=False, is_used=True) 
    
    OTP.objects.create(
        phone=phone, 
        otp_code=otp_code, 
        expires_at=expires_at,
        purpose='LOGIN'
    )
    
    # Store in cache for redundancy
    cache_key = f'otp_{phone}'
    cache.set(cache_key, otp_code, timeout=expiry_minutes * 60)
    
    # Send OTP via SMS
    send_otp_sms(phone, otp_code)
    
    return otp_code


def verify_otp(phone, otp_code):
    """
    Verify OTP code with security checks:
    - Normalization
    - Expiry (with grace period)
    - Replay prevention (is_used)
    - Try count limit
    """
    otp_code = str(otp_code).strip()
    
    logger.debug(f"VERIFYING OTP | PHONE: {phone} | ATTEMPT: {otp_code}")
    
    # Magic OTP (Strictly for Dev)
    if settings.DEBUG and otp_code == '123456':
        print("SUCCESS: Magic OTP matched")
        return True

    # 1. Look for the latest unexpired, unused OTP for this phone
    # We allow a 60s grace period for server time drift or network lag
    grace_time = timezone.now() - timezone.timedelta(seconds=60)
    
    otp_obj = OTP.objects.filter(
        phone=phone, 
        is_used=False,
        expires_at__gt=grace_time
    ).first()

    if not otp_obj:
        print("FAILURE: No active OTP record found for this phone")
        return False

    # Check attempt limit (e.g., 5 attempts)
    if otp_obj.attempt_count >= 5:
        print("FAILURE: Max attempts exceeded for this OTP")
        otp_obj.is_used = True # Burn the OTP
        otp_obj.save()
        return False

    # Compare codes (normalized)
    if otp_obj.otp_code == otp_code:
        otp_obj.is_verified = True
        otp_obj.is_used = True
        otp_obj.save()
        logger.info(f"OTP verified successfully for {phone}")
        return True
    else:
        otp_obj.attempt_count += 1
        otp_obj.save()
        logger.warning(f"OTP verification failed for {phone} (Attempt {otp_obj.attempt_count}/5)")
        return False


def send_email_otp(email):
    """Send OTP to email address"""
    otp_code = generate_otp()
    
    # Store OTP in cache with 5 minute expiry
    cache_key = f'otp_email_{email}'
    cache.set(cache_key, otp_code, timeout=300)
    
    # Send OTP via Email
    try:
        from django.core.mail import send_mail
        
        subject = 'Your Foodis Login OTP'
        message = f'Your login OTP for Foodis is {otp_code}. Valid for 5 minutes.'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]
        
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        # print(f"✅ OTP sent successfully to {email}")
        
        if settings.DEBUG:
            # print(f"\n{'='*50}")
            # print(f"🔧 DEBUG MODE: Email OTP for {email}: {otp_code}")
            # print(f"{'='*50}\n")
            pass
            
    except Exception as e:
        # print(f"❌ Error sending Email OTP: {str(e)}")
        # Fallback: print to console
        # print(f"\n\n{'#'*80}")
        # print(f"{' '*20}📧 EMAIL OTP FALLBACK 📧")
        # print(f"{' '*10}EMAIL: {email}")
        # print(f"{' '*10}OTP CODE: {otp_code}")
        # print(f"{'#'*80}\n\n")
        pass
    
    return otp_code


def verify_email_otp(email, otp_code):
    """Verify email OTP code"""
    cache_key = f'otp_email_{email}'
    stored_otp = cache.get(cache_key)
    
    if stored_otp and stored_otp == otp_code:
        cache.delete(cache_key)
        return True
    
    return False


def broadcast_order_status(order):
    """Broadcast order status update via WebSockets"""
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            f'order_{order.order_id}',
            {
                'type': 'order_status_message',
                'status': order.status,
                'timestamp': datetime.now().isoformat()
            }
        )


def broadcast_order_location(order_id, latitude, longitude):
    """Broadcast rider location update via WebSockets"""
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            f'order_{order_id}',
            {
                'type': 'order_location_message',
                'location': {
                    'latitude': float(latitude),
                    'longitude': float(longitude)
                }
            }
        )
