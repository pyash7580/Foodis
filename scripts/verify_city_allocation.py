import os
import django
import sys
from decimal import Decimal

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from core.models import City, User
from client.models import Restaurant, Order, MenuItem
from rider_legacy.models import RiderProfile

def verify():
    print("=== Verification Script: City-Based Allocation ===")
    
    # 1. Setup Test Data
    himmatnagar = City.objects.get(name='Himmatnagar')
    mehsana = City.objects.get(name='Mehsana')
    
    # Create a test client user
    client_user, _ = User.objects.get_or_create(phone='9999999999', defaults={'name': 'Test Client', 'role': 'CLIENT'})
    
    # Create a Himmatnagar Restaurant
    res_owner, _ = User.objects.get_or_create(phone='8888888888', defaults={'name': 'HNR Owner', 'role': 'RESTAURANT'})
    hnr_restaurant, _ = Restaurant.objects.get_or_create(
        owner=res_owner,
        defaults={
            'name': 'HNR Test Restaurant',
            'slug': 'hnr-test',
            'city': 'Himmatnagar',
            'city_id': himmatnagar,
            'latitude': 23.5937,
            'longitude': 72.9691,
            'status': 'APPROVED'
        }
    )
    
    # Create a Mehsana Rider
    rider_user, _ = User.objects.get_or_create(phone='7777777777', defaults={'name': 'MSN Rider', 'role': 'RIDER'})
    msn_profile, _ = RiderProfile.objects.get_or_create(
        rider=rider_user,
        defaults={
            'city': 'Mehsana',
            'city_id': mehsana,
            'is_online': True,
            'status': 'APPROVED',
            'onboarding_step': 6,
            'is_onboarding_complete': True
        }
    )
    msn_profile.is_online = True
    msn_profile.save()

    # Create a Himmatnagar Rider
    hnr_rider_user, _ = User.objects.get_or_create(phone='6666666666', defaults={'name': 'HNR Rider', 'role': 'RIDER'})
    hnr_profile, _ = RiderProfile.objects.get_or_create(
        rider=hnr_rider_user,
        defaults={
            'city': 'Himmatnagar',
            'city_id': himmatnagar,
            'is_online': True,
            'status': 'APPROVED',
            'onboarding_step': 6,
            'is_onboarding_complete': True
        }
    )
    hnr_profile.is_online = True
    hnr_profile.save()

    # Create a Himmatnagar Order
    test_order = Order.objects.create(
        user=client_user,
        restaurant=hnr_restaurant,
        city_id=himmatnagar,
        delivery_address="HNR Street",
        delivery_latitude=23.5937,
        delivery_longitude=72.9691,
        delivery_phone='9999999999',
        subtotal=100,
        total=120,
        status='READY',
        payment_method='COD',
        payment_status='PENDING'
    )
    print(f"Created Himmatnagar Order: {test_order.order_id}")

    # 2. Test Availability for Mehsana Rider
    print("\nTesting Mehsana Rider visibility...")
    from rider_legacy.views import OrderViewSet
    from rest_framework.test import APIRequestFactory, force_authenticate
    
    factory = APIRequestFactory()
    view = OrderViewSet.as_view({'get': 'available'})
    
    # Request as Mehsana Rider
    request = factory.get('/api/rider/orders/available/')
    force_authenticate(request, user=rider_user)
    response = view(request)
    
    orders = response.data
    hnr_order_visible = any(o['order']['order_id'] == test_order.order_id for o in orders if isinstance(o, dict) and 'order' in o)
    if not hnr_order_visible and not any(o['order_id'] == test_order.order_id for o in orders if isinstance(o, dict) and 'order_id' in o):
        # Check if it returned a flat list (it might if no location)
        hnr_order_visible = any(o.get('order_id') == test_order.order_id for o in orders if isinstance(o, dict))

    if not hnr_order_visible:
        print("SUCCESS: Himmatnagar order is NOT visible to Mehsana rider.")
    else:
        print("FAILURE: Himmatnagar order is visible to Mehsana rider!")

    # 3. Test Availability for Himmatnagar Rider
    print("\nTesting Himmatnagar Rider visibility...")
    request = factory.get('/api/rider/orders/available/')
    force_authenticate(request, user=hnr_rider_user)
    response = view(request)
    
    orders = response.data
    # Handling response format (nearby_orders vs flat list)
    hnr_order_visible = False
    if isinstance(orders, list):
        for o in orders:
            if isinstance(o, dict):
                if 'order' in o and o['order']['order_id'] == test_order.order_id:
                    hnr_order_visible = True
                    break
                if o.get('order_id') == test_order.order_id:
                    hnr_order_visible = True
                    break

    if hnr_order_visible:
        print("SUCCESS: Himmatnagar order IS visible to Himmatnagar rider.")
    else:
        print("FAILURE: Himmatnagar order is NOT visible to Himmatnagar rider!")

    # 4. Cleanup
    test_order.delete()
    print("\nVerification completed.")

if __name__ == "__main__":
    verify()
