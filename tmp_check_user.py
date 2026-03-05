
import os
import django
import sys

# Set up Django environment
sys.path.append('d:\\Foodis')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

email = "nawab-delight@foodis.local"
user = User.objects.filter(email__iexact=email).first()

if user:
    print(f"User found: {user.email}")
    print(f"Role: {user.role}")
    print(f"Is active: {user.is_active}")
    # We can't easily check password here without the plain text, 
    # but we can check if it matches 'Nawab@'
    if user.check_password("Nawab@"):
        print("Password 'Nawab@' is CORRECT")
    else:
        print("Password 'Nawab@' is INCORRECT")
else:
    print(f"User NOT found: {email}")

# Also check for the misspelled one just in case
email_misspelled = "nawab-delight@foodis.loca"
user_misspelled = User.objects.filter(email__iexact=email_misspelled).first()
if user_misspelled:
    print(f"User found with MISSPELLED email: {user_misspelled.email}")
else:
    print(f"User NOT found with misspelled email: {email_misspelled}")
