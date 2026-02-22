#!/usr/bin/env python
import os
import django
from collections import defaultdict
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from core.models import User

print("=" * 80)
print("DIAGNOSTIC: User Database Analysis")
print("=" * 80)

# Get all users
all_users = User.objects.all()
total_users = all_users.count()

print(f"\nTotal users in database: {total_users}")

if total_users == 0:
    print("[ERROR] No users found in database!")
    exit(1)

# Categorize users by role
users_by_role = defaultdict(list)
for user in all_users:
    users_by_role[user.role].append(user)

print("\nUsers by role:")
for role in ['CLIENT', 'RESTAURANT', 'RIDER', 'ADMIN']:
    count = len(users_by_role.get(role, []))
    print(f"  - {role}: {count}")

# Analyze phone number formats
print("\n" + "=" * 80)
print("PHONE NUMBER ANALYSIS")
print("=" * 80)

phone_formats = defaultdict(list)
missing_phone = []
missing_role = []

for user in all_users:
    # Check for missing role
    if not user.role:
        missing_role.append(user)

    # Analyze phone format
    if not user.phone or user.phone.strip() == '':
        missing_phone.append(user)
    else:
        phone = user.phone.strip()

        if phone.startswith('+91'):
            if phone.startswith('+91 ') or '+91-' in phone or '+91(' in phone:
                phone_formats['Format "+91 XXXXXXXXXX" (with spaces)'].append(user)
            else:
                phone_formats['Format "+91XXXXXXXXXX" (correct)'].append(user)
        elif phone.startswith('91'):
            if len(phone) == 12:
                phone_formats['Format "91XXXXXXXXXX" (12 digits)'].append(user)
            else:
                phone_formats[f'Format "91..." (variable length: {len(phone)})'].append(user)
        elif phone.startswith('9'):
            if len(phone) == 10:
                phone_formats['Format "9XXXXXXXXX" (10 digits, missing +91)'].append(user)
            else:
                phone_formats[f'Format "9..." (variable length: {len(phone)})'].append(user)
        else:
            phone_formats['Format "Other" (unexpected format)'].append(user)

print(f"\nPhone format distribution:")
for fmt, users in sorted(phone_formats.items(), key=lambda x: -len(x[1])):
    print(f"  {fmt}: {len(users)} users")

if missing_phone:
    print(f"\n  [ISSUE] Missing phone entirely: {len(missing_phone)} users")
    for user in missing_phone[:5]:  # Show first 5
        print(f"    - {user.name or user.email} (ID: {user.id})")

if missing_role:
    print(f"\n  [ISSUE] Missing role: {len(missing_role)} users")
    for user in missing_role[:5]:  # Show first 5
        print(f"    - {user.name or user.email} (ID: {user.id})")

# Analyze email
print("\n" + "=" * 80)
print("EMAIL ANALYSIS")
print("=" * 80)

has_email = len([u for u in all_users if u.email and u.email.strip()])
missing_email = total_users - has_email

print(f"\nUsers with email: {has_email}/{total_users}")
print(f"Users without email: {missing_email}/{total_users}")

# Test user lookup scenarios
print("\n" + "=" * 80)
print("USER LOOKUP TEST")
print("=" * 80)

# Pick a user from most common format
def normalize_phone(phone):
    """Normalize phone number like the backend should do"""
    if not phone:
        return None
    phone = phone.strip()
    phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    if phone.startswith('+91'):
        phone = phone[3:]
    if len(phone) == 10 and phone[0] == '9':
        return f"+91{phone}"
    return phone

# Test each format in database
lookup_results = defaultdict(int)
found_count = 0
not_found_count = 0

for user in all_users:
    if not user.phone:
        continue

    # Try to find user by normalized phone
    normalized = normalize_phone(user.phone)
    if normalized:
        found = User.objects.filter(phone=normalized).exists()
        if found:
            found_count += 1
            lookup_results['Found by normalized phone'] += 1
        else:
            not_found_count += 1
            lookup_results['NOT FOUND by normalized phone'] += 1
            print(f"  [NOT FOUND] Phone: {user.phone} → Normalized: {normalized}")
    else:
        not_found_count += 1
        lookup_results['Cannot normalize phone'] += 1
        print(f"  [CANNOT NORMALIZE] Phone: {user.phone}")

print(f"\nLookup results:")
for result, count in sorted(lookup_results.items(), key=lambda x: -x[1]):
    print(f"  {result}: {count}")

# Summary
print("\n" + "=" * 80)
print("SUMMARY & RECOMMENDATIONS")
print("=" * 80)

issues_found = False

if missing_phone:
    print(f"\n[ISSUE 1] {len(missing_phone)} users have no phone number")
    print("  Action: These users cannot log in via phone-based OTP")
    print("  - Need to add phone numbers to these users")
    issues_found = True

if missing_role:
    print(f"\n[ISSUE 2] {len(missing_role)} users have no role")
    print("  Action: Default to 'CLIENT' role for these users")
    issues_found = True

if not_found_count > 0:
    print(f"\n[ISSUE 3] {not_found_count} users cannot be found by normalized phone")
    print("  Action: Normalize phone numbers in the database")
    issues_found = True

if has_email < total_users * 0.5:
    print(f"\n[ISSUE 4] Only {has_email}/{total_users} users have email")
    print("  Action: Email login may fail for users without email")
    issues_found = True

if not issues_found:
    print("\n[OK] No critical issues found!")
    print("Users should be able to log in.")
else:
    print("\n" + "=" * 80)
    print("ACTION REQUIRED:")
    print("Run: python fix_users.py")
    print("=" * 80)

print("\n")
