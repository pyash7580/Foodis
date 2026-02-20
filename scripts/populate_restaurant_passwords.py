import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from client.models import Restaurant

def populate_restaurant_passwords():
    print("Populating restaurant passwords...")
    
    restaurants = Restaurant.objects.all()
    updated_count = 0
    
    for restaurant in restaurants:
        # Defaults for demo
        restaurant.password_plain = "password123"
        restaurant.save()
        updated_count += 1
            
    print(f"Successfully updated passwords for {updated_count} restaurants to 'password123'.")

if __name__ == "__main__":
    populate_restaurant_passwords()
