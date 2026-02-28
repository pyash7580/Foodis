#!/usr/bin/env python
"""
Import all restaurants and dishes from all_dishes_data.py into the database.
- Creates/updates Restaurant with specific name and location (city).
- Creates MenuItem for each dish with name, type (VEG/NON_VEG), and price.
- Uses a default Category "Main" for all dishes.
- Image: dish image field is left blank. Add images via Django admin (edit each MenuItem)
  or use a bulk upload script later. Frontend can show a placeholder when image is null.

Run from project root: python scripts/import_all_restaurants_dishes.py
"""
import os
import sys
import re
from pathlib import Path
from decimal import Decimal

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from client.models import Restaurant, MenuItem, Category
from core.models import City

User = get_user_model()
DEFAULT_PASSWORD = os.environ.get('DEFAULT_LOGIN_PASSWORD', 'Password123')

# City coordinates for Mehsana / Himmatnagar
CITY_COORDS = {
    'Mehsana': (Decimal('23.5880'), Decimal('72.3693')),
    'Himmatnagar': (Decimal('23.5937'), Decimal('72.9691')),
}


def slugify(s):
    s = re.sub(r'[^\w\s-]', '', s).strip().lower()
    return re.sub(r'[-\s]+', '-', s)[:50]


def get_or_create_category(name='Main'):
    slug = slugify(name) or 'main'
    cat, _ = Category.objects.get_or_create(slug=slug, defaults={'name': name, 'is_active': True})
    return cat


def get_or_create_city(name):
    city, _ = City.objects.get_or_create(name=name, defaults={'is_active': True})
    return city


def run():
    from scripts.all_dishes_data import RESTAURANTS_DATA

    default_cat = get_or_create_category('Main')
    total_dishes = 0
    rest_created = 0
    rest_updated = 0

    for idx, data in enumerate(RESTAURANTS_DATA):
        name = (data.get('name') or '').strip()
        location = (data.get('location') or 'Mehsana').strip()
        dishes_list = data.get('dishes') or []
        if not name:
            continue

        city_obj = get_or_create_city(location)
        lat, lng = CITY_COORDS.get(location, CITY_COORDS['Mehsana'])

        # Find or create restaurant by name (and city to avoid clashes)
        restaurant = Restaurant.objects.filter(name__iexact=name).first()
        if not restaurant:
            restaurant = Restaurant.objects.filter(name__icontains=name, city__iexact=location).first()
        if restaurant:
            restaurant.name = name
            restaurant.city = location
            restaurant.city_id = city_obj
            restaurant.latitude = lat
            restaurant.longitude = lng
            restaurant.status = 'APPROVED'
            restaurant.is_active = True
            restaurant.save()
            rest_updated += 1
        else:
            slug = slugify(name)
            base_slug = slug or f'restaurant-{idx}'
            slug = base_slug
            n = 0
            while Restaurant.objects.filter(slug=slug).exists():
                n += 1
                slug = f'{base_slug}-{n}'
            email = f"{slug}@foodis.local"
            owner = User.objects.filter(email__iexact=email).first()
            if not owner:
                owner = User.objects.create(
                    email=email,
                    name=f"Owner of {name}",
                    role='RESTAURANT',
                    is_active=True,
                    is_verified=True,
                )
                owner.set_password(DEFAULT_PASSWORD)
                owner.save(update_fields=['password'])
            restaurant = Restaurant.objects.create(
                owner=owner,
                name=name,
                slug=slug,
                email=owner.email,
                password=make_password(DEFAULT_PASSWORD),
                address=f"{name}, {location}",
                city=location,
                city_id=city_obj,
                state='Gujarat',
                pincode='384001',
                latitude=lat,
                longitude=lng,
                status='APPROVED',
                is_active=True,
                cuisine=data.get('cuisine') or 'Multi',
                delivery_fee=Decimal('30.00'),
                min_order_amount=Decimal('100.00'),
            )
            rest_created += 1

        for d in dishes_list:
            dish_name = (d.get('name') or '').strip()
            if not dish_name:
                continue
            veg_type = (d.get('type') or 'VEG').strip().upper()
            if veg_type not in ('VEG', 'NON_VEG', 'EGG'):
                veg_type = 'VEG'
            try:
                price = Decimal(str(d.get('price', '0')))
            except Exception:
                price = Decimal('99.00')

            item, created = MenuItem.objects.get_or_create(
                restaurant=restaurant,
                name=dish_name,
                defaults={
                    'price': price,
                    'veg_type': veg_type,
                    'category': default_cat,
                    'is_available': True,
                }
            )
            if not created:
                item.price = price
                item.veg_type = veg_type
                item.is_available = True
                item.save(update_fields=['price', 'veg_type', 'is_available'])
            total_dishes += 1

    print(f"Done. Restaurants created: {rest_created}, updated: {rest_updated}")
    print(f"Total menu items created/updated: {total_dishes}")


if __name__ == '__main__':
    run()
