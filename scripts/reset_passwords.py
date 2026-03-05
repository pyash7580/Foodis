"""
Script: reset_passwords.py
Run with: python manage.py shell < scripts/reset_passwords.py

Resets restaurant and rider passwords to match LOGIN_CREDENTIALS.md:
- Restaurants: first word of slug capitalized + '@'  (e.g. 'Biryani@')
- Riders: first name capitalized + '@'               (e.g. 'Rakesh@')
- Admin: admin@foodis.com → 'admin@123'
"""
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')

from django.contrib.auth import get_user_model

User = get_user_model()

reset_count = 0
errors = []

# ── Admin ──────────────────────────────────────────────────────────────────
admin = User.objects.filter(email='admin@foodis.com').first()
if admin:
    admin.set_password('admin@123')
    admin.save(update_fields=['password'])
    print(f'✅ Admin: admin@foodis.com → admin@123')
    reset_count += 1

# ── Restaurants ────────────────────────────────────────────────────────────
# Password pattern: first word of email slug capitalized + '@'
# email format: <slug>@foodis.local  e.g. biryani-boulevard@foodis.local → 'Biryani@'
restaurant_users = User.objects.filter(role='RESTAURANT')
for user in restaurant_users:
    try:
        slug = user.email.split('@')[0]           # e.g. 'biryani-boulevard'
        first_word = slug.split('-')[0].capitalize()  # → 'Biryani'
        password = first_word + '@'               # → 'Biryani@'

        # Special cases from LOGIN_CREDENTIALS.md
        special_cases = {
            'restaurant_owner@example.com': 'Tasty@',
            'test_restaurant@example.com': 'Restaurant@',
        }
        if user.email in special_cases:
            password = special_cases[user.email]

        user.set_password(password)
        user.save(update_fields=['password'])
        print(f'✅ Restaurant: {user.email} → {password}')
        reset_count += 1
    except Exception as e:
        errors.append(f'❌ {user.email}: {e}')

# ── Riders ─────────────────────────────────────────────────────────────────
# Password pattern: first name of rider capitalized + '@'
# email format: firstname.lastname@foodis.com  e.g. rakesh.kumar@foodis.com → 'Rakesh@'
rider_users = User.objects.filter(role='RIDER')
for user in rider_users:
    try:
        local = user.email.split('@')[0]            # e.g. 'rakesh.kumar'
        first_name = local.split('.')[0].capitalize()   # → 'Rakesh'
        password = first_name + '@'                 # → 'Rakesh@'
        user.set_password(password)
        user.save(update_fields=['password'])
        print(f'✅ Rider: {user.email} → {password}')
        reset_count += 1
    except Exception as e:
        errors.append(f'❌ {user.email}: {e}')

print(f'\n{"="*50}')
print(f'Total passwords reset: {reset_count}')
if errors:
    print(f'Errors ({len(errors)}):')
    for e in errors:
        print(f'  {e}')
else:
    print('No errors!')
