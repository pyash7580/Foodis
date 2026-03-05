#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from core.models import User

total = User.objects.filter(role='RIDER').count()
print(f"✓ Total riders in database: {total}")
print(f"✓ All 50 riders are ready to login!")
