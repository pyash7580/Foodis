"""
Core Services Package

Houses all core service modules including email, OTP, and authentication services.
"""

from .email_service import send_email_otp, verify_email_otp, generate_otp, get_otp_status

__all__ = [
    'send_email_otp',
    'verify_email_otp', 
    'generate_otp',
    'get_otp_status',
]
