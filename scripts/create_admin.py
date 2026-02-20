import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.management import call_command

User = get_user_model()

def create_super_admin():
    """Create default Super Admin if not exists"""
    ADMIN_PHONE = '+910000000000' # Dummy phone for admin
    ADMIN_EMAIL = 'admin@foodis.com'
    ADMIN_PASS = 'admin123'
    
    try:
        if not User.objects.filter(phone=ADMIN_PHONE).exists():
            print("Creating Super Admin user...")
            admin = User.objects.create_superuser(
                phone=ADMIN_PHONE,
                email=ADMIN_EMAIL,
                password=ADMIN_PASS,
                name='Super Admin',
                role='ADMIN'
            )
            print(f"✅ Super Admin created successfully!")
            print(f"   Username: admin (mapped to {ADMIN_PHONE})") # Frontend will handle 'admin' -> phone mapping or we allow email login
            print(f"   Email: {ADMIN_EMAIL}")
            print(f"   Password: {ADMIN_PASS}")
        else:
            print("ℹ️ Super Admin already exists.")
            # Ensure checks
            admin = User.objects.get(phone=ADMIN_PHONE)
            if not admin.is_superuser or not admin.is_staff or admin.role != 'ADMIN':
                print("   Updating permissions...")
                admin.is_superuser = True
                admin.is_staff = True
                admin.role = 'ADMIN'
                admin.save()
                print("   ✅ Permissions updated.")

    except Exception as e:
        print(f"❌ Error creating admin: {str(e)}")

if __name__ == '__main__':
    create_super_admin()
