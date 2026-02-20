import requests
import sys
import os
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from client.models import Restaurant, User
from rest_framework.test import APIRequestFactory, force_authenticate
from admin_panel.views import RestaurantViewSet

def test_admin_cover_update():
    # 1. Get an admin user
    admin = User.objects.filter(role='ADMIN').first()
    if not admin:
        print("No admin user found.")
        return

    # 2. Get a target restaurant (The Vintage Kitchen)
    restaurant = Restaurant.objects.filter(name__icontains="Vintage").first()
    if not restaurant:
        print("Restaurant not found.")
        return
        
    print(f"Testing update for: {restaurant.name}")
    print(f"Current Cover: {restaurant.cover_image}")

    # 3. Simulate API call
    factory = APIRequestFactory()
    view = RestaurantViewSet.as_view({'patch': 'partial_update'})
    
    # We won't actually change the file content, just send the request with a dummy field to check if it 200s
    # Or actually, let's try to update the description slightly to verify 'patch' works
    original_desc = restaurant.description or ""
    new_desc = original_desc + " "
    
    data = {'description': new_desc}
    
    request = factory.patch(f'/api/admin/restaurants/{restaurant.id}/', data, format='json')
    force_authenticate(request, user=admin)
    
    response = view(request, pk=restaurant.id)
    print(f"Response Status: {response.status_code}")
    print(f"Response Data keys: {response.data.keys() if hasattr(response, 'data') else 'No data'}")
    
    if response.status_code == 200:
        print("Admin API supports partial update.")
    else:
        print("Admin API failed to update.")
        print(response.data)

if __name__ == "__main__":
    test_admin_cover_update()
