#!/usr/bin/env python
"""
Migration Helper Script for Email-Based Authentication System

This script helps manage Django migrations for the email authentication overhaul.
Run this before deploying to ensure all database changes are applied.

Usage:
    python migration_helper.py make       # Create migrations
    python migration_helper.py migrate    # Apply migrations
    python migration_helper.py status     # Check migration status
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
sys.path.insert(0, str(Path(__file__).parent))
django.setup()

from django.core.management import call_command
from django.db import connection
from django.apps import apps

def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def check_migrations():
    """Check if migrations need to be created"""
    print_header("Checking Migration Status")
    try:
        call_command('showmigrations', '--plan')
        print("\n✓ Migration status displayed above")
        return True
    except Exception as e:
        print(f"✗ Error checking migrations: {e}")
        return False

def make_migrations():
    """Create new migrations"""
    print_header("Creating Migrations")
    try:
        call_command('makemigrations')
        print("\n✓ Migrations created successfully")
        return True
    except Exception as e:
        print(f"✗ Error creating migrations: {e}")
        return False

def apply_migrations():
    """Apply pending migrations"""
    print_header("Applying Migrations")
    try:
        call_command('migrate')
        print("\n✓ Migrations applied successfully")
        return True
    except Exception as e:
        print(f"✗ Error applying migrations: {e}")
        return False

def verify_models():
    """Verify model changes"""
    print_header("Verifying Model Changes")
    try:
        from core.models import User, OTP
        from client.models import Restaurant
        from rider.models import Rider
        
        print("✓ User model:")
        print(f"  - EMAIL field: {any(f.name == 'email' for f in User._meta.get_fields())}")
        print(f"  - USERNAME_FIELD: {User.USERNAME_FIELD}")
        
        print("✓ Restaurant model:")
        print(f"  - EMAIL field (unique): {Restaurant._meta.get_field('email').unique}")
        print(f"  - PASSWORD field: {any(f.name == 'password' for f in Restaurant._meta.get_fields())}")
        
        print("✓ Rider model:")
        print(f"  - EMAIL field (unique): {Rider._meta.get_field('email').unique}")
        print(f"  - PASSWORD field: {any(f.name == 'password' for f in Rider._meta.get_fields())}")
        
        print("✓ OTP model:")
        print(f"  - EMAIL field: {any(f.name == 'email' for f in OTP._meta.get_fields())}")
        
        return True
    except Exception as e:
        print(f"✗ Error verifying models: {e}")
        return False

def test_email_service():
    """Test email service configuration"""
    print_header("Testing Email Service")
    try:
        from django.conf import settings
        from core.services.email_service import send_email_otp
        
        print(f"Email Backend: {settings.EMAIL_BACKEND}")
        print(f"Email Host: {settings.EMAIL_HOST}")
        print(f"Email Port: {settings.EMAIL_PORT}")
        print(f"Email From: {settings.EMAIL_FROM}")
        print(f"OTP Expiry: {settings.OTP_EXPIRY_MINUTES} minutes")
        
        if not settings.EMAIL_HOST_PASSWORD:
            print("⚠ WARNING: EMAIL_HOST_PASSWORD is not configured!")
            print("  OTP will be printed to console only. For real email, set in .env:")
            print("  EMAIL_HOST_PASSWORD=your_sendgrid_api_key")
            return False
        
        print("\n✓ Email service is configured")
        return True
    except Exception as e:
        print(f"✗ Error testing email service: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python migration_helper.py [command]")
        print("\nCommands:")
        print("  make      - Create migrations")
        print("  migrate   - Apply migrations")
        print("  status    - Check migration status")
        print("  verify    - Verify model changes")
        print("  test-email - Test email configuration")
        print("  full      - Run all steps (make → migrate → verify → test-email)")
        return

    command = sys.argv[1].lower()

    if command == 'make':
        make_migrations()
    elif command == 'migrate':
        apply_migrations()
    elif command == 'status':
        check_migrations()
    elif command == 'verify':
        verify_models()
    elif command == 'test-email':
        test_email_service()
    elif command == 'full':
        check_migrations()
        if input("\nCreate migrations? (y/n): ").lower() == 'y':
            if make_migrations():
                if input("Apply migrations? (y/n): ").lower() == 'y':
                    if apply_migrations():
                        verify_models()
                        test_email_service()
    else:
        print(f"Unknown command: {command}")

if __name__ == '__main__':
    main()
