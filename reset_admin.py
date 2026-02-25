import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

def create_admin():
    phone = "9824949865"
    password = "adminpassword123"
    
    user, created = User.objects.get_or_create(
        phone=phone,
        defaults={
            'name': 'Admin User',
            'role': 'ADMIN',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.role = 'ADMIN'
    user.save()
    
    if created:
        print(f"✅ Successfully created new Admin with Phone: {phone} and Password: {password}")
    else:
        print(f"✅ Successfully reset Password for Phone: {phone} to: {password}")

if __name__ == "__main__":
    create_admin()
