#!/usr/bin/env python
"""
Remove only the generic-named restaurants: "Restaurant 1", "Restaurant 2", ... "Restaurant 53".
Keeps all other restaurants (Biryani Boulevard, Bombay Brasserie, popes cafe, etc.) and their data.
Also deletes the owner User accounts for those removed restaurants.
"""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from client.models import Restaurant

User = get_user_model()

def run():
    to_delete = []
    for n in range(1, 54):  # 1 to 53
        name = f"Restaurant {n}"
        r = Restaurant.objects.filter(name=name).first()
        if r:
            to_delete.append(r)

    owners_to_delete = [r.owner_id for r in to_delete]
    for r in to_delete:
        r.delete()  # cascades to menu_items
    deleted_rest = len(to_delete)

    for uid in owners_to_delete:
        User.objects.filter(id=uid).delete()
    print(f"Removed {deleted_rest} restaurants (Restaurant 1 through Restaurant 53) and their owner accounts.")
    print(f"Remaining approved restaurants: {Restaurant.objects.filter(status='APPROVED', is_active=True).count()}")

if __name__ == '__main__':
    run()
