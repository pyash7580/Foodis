#!/usr/bin/env python
"""
Set email and password for all EXISTING restaurants and riders in the database.
Does NOT create new Restaurant or Rider records - only updates existing ones so
they can log in with email + password.

- Restaurants: updates owner (core.User) email + password, and Restaurant.email.
- Riders: ensures core.User exists for each Rider (get_or_create by email),
  sets password on User and on Rider model.

Usage:
  python scripts/set_restaurant_rider_login_credentials.py
  python scripts/set_restaurant_rider_login_credentials.py --password MySecurePass

Output:
  - Updates database (no new restaurants/riders created).
  - Writes RESTAURANT_LOGIN_CREDENTIALS.csv and RIDER_LOGIN_CREDENTIALS.csv in project root.
"""

import os
import sys
import csv
import argparse
from pathlib import Path

# Django setup
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from client.models import Restaurant
from rider.models import Rider
from django.contrib.auth.hashers import make_password

User = get_user_model()
DEFAULT_PASSWORD = 'Password123'


def slug_to_email(slug, suffix='@foodis.local'):
    """Generate a valid email from slug (e.g. my-restaurant -> my-restaurant@foodis.local)."""
    if not slug:
        return None
    base = slug.replace(' ', '-').lower()[:50]
    return base + suffix


def run(default_password=None):
    password = default_password or os.environ.get('DEFAULT_LOGIN_PASSWORD', DEFAULT_PASSWORD)

    restaurant_creds = []
    rider_creds = []

    # ---- Restaurants (only existing; update owner User + Restaurant.email) ----
    restaurants = Restaurant.objects.all().select_related('owner')
    print(f"Found {restaurants.count()} existing restaurants. Updating owner email + password...")
    for r in restaurants:
        try:
            owner = r.owner
            if not owner.email or not owner.email.strip():
                email = (r.email and r.email.strip()) or slug_to_email(getattr(r, 'slug', None)) or f"restaurant{r.pk}@foodis.local"
                owner.email = email
            else:
                email = owner.email.strip().lower()
                owner.email = email
            owner.set_password(password)
            owner.save(update_fields=['email', 'password'])
            r.email = owner.email
            r.save(update_fields=['email'])
            restaurant_creds.append((email, password))
        except Exception as e:
            print(f"  Restaurant id={r.pk} ({getattr(r, 'name', '')}): {e}")
    print(f"  Updated {len(restaurant_creds)} restaurants.\n")

    # ---- Riders (only existing; ensure User exists, set password on User and Rider) ----
    riders = Rider.objects.all()
    print(f"Found {riders.count()} existing riders. Ensuring User + password for each...")
    for rider in riders:
        try:
            email = (rider.email or '').strip()
            if not email:
                email = f"rider{rider.pk}@foodis.local"
                rider.email = email
                rider.save(update_fields=['email'])
            email = email.lower()
            user = User.objects.filter(email__iexact=email).first()
            if not user:
                user = User.objects.create(
                    email=email,
                    name=getattr(rider, 'full_name', '') or f"Rider {rider.pk}",
                    role='RIDER',
                    is_active=True,
                    is_verified=True,
                )
            user.set_password(password)
            user.save(update_fields=['password'])
            rider.password = make_password(password)
            rider.save(update_fields=['password', 'email'])
            rider_creds.append((email, password))
        except Exception as e:
            print(f"  Rider id={rider.pk} ({getattr(rider, 'full_name', '')}): {e}")
    print(f"  Updated {len(rider_creds)} riders.\n")

    # ---- Write CSV files ----
    out_dir = PROJECT_ROOT
    rest_path = out_dir / 'RESTAURANT_LOGIN_CREDENTIALS.csv'
    rider_path = out_dir / 'RIDER_LOGIN_CREDENTIALS.csv'
    with open(rest_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['email', 'password'])
        w.writerows(restaurant_creds)
    with open(rider_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['email', 'password'])
        w.writerows(rider_creds)
    print(f"Credentials written to:\n  {rest_path}\n  {rider_path}")
    print(f"Restaurants: {len(restaurant_creds)} | Riders: {len(rider_creds)}")
    return len(restaurant_creds), len(rider_creds)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Set email+password for existing restaurants and riders')
    parser.add_argument('--password', type=str, default=None, help='Password to set for all (default: Password123)')
    args = parser.parse_args()
    run(default_password=args.password)
