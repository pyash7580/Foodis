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






def send_email_otp(email):
    """Send OTP to email address"""
    otp_code = generate_otp()
    
    cache_key = f'otp_email_{email}'
    try:
        cache.set(cache_key, otp_code, timeout=300)
    except Exception as cache_err:
        logger.warning(f"Email OTP cache set skipped for {email}: {cache_err}")
    
    try:
        from django.core.mail import send_mail
        
        subject = 'Your Foodis Login OTP'
        message = f'Your login OTP for Foodis is {otp_code}. Valid for 5 minutes.'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]
        
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            
    except Exception as e:
        pass
    
    return otp_code


def verify_email_otp(email, otp_code):
    """Verify email OTP code"""
    cache_key = f'otp_email_{email}'
    try:
        stored_otp = cache.get(cache_key)
    except Exception as cache_err:
        logger.warning(f"Email OTP cache get failed for {email}: {cache_err}")
        stored_otp = None
    
    if stored_otp and stored_otp == otp_code:
        try:
            cache.delete(cache_key)
        except Exception as cache_err:
            logger.warning(f"Email OTP cache delete skipped for {email}: {cache_err}")
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
