#!/usr/bin/env python
"""
Seed the database so that 53 restaurants and 395 riders exist (and show) with email + password.
Only CREATES the shortfall: if you already have 5 restaurants, it creates 48 more to reach 53.
Does not delete or replace existing data.

Run after: python scripts/set_restaurant_rider_login_credentials.py
to set the same password for all (or run that script after to set passwords).

Usage:
  python scripts/seed_53_restaurants_395_riders.py
"""
import os
import sys
from pathlib import Path
from decimal import Decimal

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from client.models import Restaurant
from rider.models import Rider
from core.models import City

User = get_user_model()
TARGET_RESTAURANTS = 53
TARGET_RIDERS = 395
DEFAULT_PASSWORD = os.environ.get('DEFAULT_LOGIN_PASSWORD', 'Password123')
CITIES = ['Mehsana', 'Himmatnagar']


def get_or_create_city(name):
    city, _ = City.objects.get_or_create(name=name, defaults={'is_active': True})
    return city


def seed_restaurants():
    current = Restaurant.objects.count()
    need = max(0, TARGET_RESTAURANTS - current)
    if need == 0:
        print(f"Restaurants: already {current} (target {TARGET_RESTAURANTS}). Skip.")
        return 0
    print(f"Restaurants: {current} exist, creating {need} more (target {TARGET_RESTAURANTS})...")
    created = 0
    for i in range(need):
        idx = current + i + 1
        email = f"restaurant{idx}@foodis.local"
        if User.objects.filter(email__iexact=email).exists():
            email = f"restaurant_{idx}_{current}_{i}@foodis.local"
        slug = f"restaurant-{idx}-{i}"
        while Restaurant.objects.filter(slug=slug).exists():
            slug = f"restaurant-{idx}-{i}-{created}"
        owner = User.objects.create(
            email=email,
            name=f"Restaurant Owner {idx}",
            role='RESTAURANT',
            is_active=True,
            is_verified=True,
        )
        owner.set_password(DEFAULT_PASSWORD)
        owner.save(update_fields=['password'])
        city_name = CITIES[i % len(CITIES)]
        city = get_or_create_city(city_name)
        Restaurant.objects.create(
            owner=owner,
            name=f"Restaurant {idx}",
            slug=slug,
            email=owner.email,
            password=make_password(DEFAULT_PASSWORD),
            address=f"Address {idx}, {city_name}",
            city=city_name,
            city_id=city,
            state="Gujarat",
            pincode="384001",
            latitude=Decimal("23.5880") if city_name == 'Mehsana' else Decimal("23.5937"),
            longitude=Decimal("72.3693") if city_name == 'Mehsana' else Decimal("72.9691"),
            status='APPROVED',
            is_active=True,
            cuisine="Multi",
            delivery_fee=Decimal("30.00"),
            min_order_amount=Decimal("100.00"),
        )
        created += 1
    print(f"  Created {created} restaurants. Total now: {Restaurant.objects.count()}")
    return created


def seed_riders():
    current = Rider.objects.count()
    need = max(0, TARGET_RIDERS - current)
    if need == 0:
        print(f"Riders: already {current} (target {TARGET_RIDERS}). Skip.")
        return 0
    print(f"Riders: {current} exist, creating {need} more (target {TARGET_RIDERS})...")
    created = 0
    for i in range(need):
        idx = current + i + 1
        email = f"rider{idx}@foodis.local"
        while Rider.objects.filter(email__iexact=email).exists() or User.objects.filter(email__iexact=email).exists():
            email = f"rider_{idx}_{i}_{created}@foodis.local"
        city_name = CITIES[i % len(CITIES)]
        rider = Rider.objects.create(
            email=email,
            full_name=f"Rider {idx}",
            password=make_password(DEFAULT_PASSWORD),
            is_active=True,
            city=city_name,
        )
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            user = User.objects.create(
                email=email,
                name=rider.full_name,
                role='RIDER',
                is_active=True,
                is_verified=True,
            )
            user.set_password(DEFAULT_PASSWORD)
            user.save(update_fields=['password'])
        created += 1
    print(f"  Created {created} riders. Total now: {Rider.objects.count()}")
    return created


def main():
    print("Target: 53 restaurants, 395 riders (with email + password).\n")
    seed_restaurants()
    print()
    seed_riders()
    print("\nDone. Run: python scripts/set_restaurant_rider_login_credentials.py --password Password123")
    print("to ensure all have the same login password and to generate CSV files.")


if __name__ == '__main__':
    main()
