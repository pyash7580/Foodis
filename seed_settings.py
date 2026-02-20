import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from admin_panel.models import SystemSettings

DEFAULTS = {
    "site_info": {
        "value": json.dumps({
            "name": "Foodis",
            "description": "Premium Food Delivery",
            "maintenance_mode": False
        }),
        "description": "General site information"
    },
    "finance": {
        "value": json.dumps({
            "currency": "INR",
            "tax_rate": 5.0,
            "platform_fee": 15.0,
            "delivery_charge_base": 20.0,
            "delivery_charge_per_km": 5.0,
            "min_order_amount": 100.0
        }),
        "description": "Financial settings, taxes, and fees"
    },
    "contact": {
        "value": json.dumps({
            "email": "support@foodis.com",
            "phone": "+91 9876543210",
            "address": "123 Food Street, Tech Park, India"
        }),
        "description": "Contact details for support"
    },
    "app_links": {
        "value": json.dumps({
            "android": "https://play.google.com/store/apps/details?id=com.foodis",
            "ios": "https://apps.apple.com/app/foodis/id123456789",
            "facebook": "https://facebook.com/foodis",
            "instagram": "https://instagram.com/foodis"
        }),
        "description": "Mobile app and social media links"
    }
}

def seed_settings():
    print("--- Seeding System Settings ---")
    for key, data in DEFAULTS.items():
        obj, created = SystemSettings.objects.get_or_create(key=key)
        if created:
            obj.value = data['value']
            obj.description = data['description']
            obj.save()
            print(f"Created setting: {key}")
        else:
            print(f"Setting {key} already exists.")

if __name__ == '__main__':
    seed_settings()
