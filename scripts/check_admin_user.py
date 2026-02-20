
import os
import django
import sys

# Add the project root to the python path
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

try:
    # Find superuser
    admins = User.objects.filter(is_superuser=True)
    
    if admins.exists():
        print(f"Found {admins.count()} superuser(s):")
        for admin in admins:
            print(f"---")
            print(f"Name: {admin.name}")
            print(f"Email: {admin.email}")
            print(f"Phone: {admin.phone}")
            print(f"Active: {admin.is_active}")
            # Check 'admin' password availability
            print(f"Password 'admin' valid: {admin.check_password('admin')}")
            print(f"Password 'admin123' valid: {admin.check_password('admin123')}")
    else:
        print("No superusers found.")

except Exception as e:
    print(f"Error: {e}")
