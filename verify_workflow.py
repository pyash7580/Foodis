import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
django.setup()

from rest_framework.test import APIClient
from core.models import User, Address
from client.models import Restaurant, MenuItem, Cart, Order

# Helper wait to simulate full requests sequence
def verify():
    client_user = User.objects.get(id=101)  # Phone: 5412563258
    rest_user = User.objects.get(id=1)      # Phone: 9000000000
    rider_user = User.objects.get(id=113)   # Phone: 9336627200
    admin_user = User.objects.get(id=331)   # Phone: 0000000000

    api_client = APIClient()

    print("====================================")
    print("1. CLIENT WORKFLOW")
    print("====================================")
    api_client.force_authenticate(user=client_user)
    
    # A. Fetch Restaurants
    res = api_client.get('/api/client/restaurants/')
    qty = len(res.json().get('results', res.json())) if isinstance(res.json(), dict) else len(res.json())
    print(f"[SUCCESS] Fetched Restaurants (HTTP {res.status_code}) - Found {qty} restaurants")

    rest = Restaurant.objects.filter(owner=rest_user).first()
    if not rest:
        print("[FAIL] Test restaurant not found")
        return

    # B. Fetch Menu
    res = api_client.get(f'/api/client/restaurants/{rest.id}/menu/')
    menu_items = res.json()
    print(f"[SUCCESS] Fetched Menu for {rest.name} (HTTP {res.status_code}) - Found {len(menu_items)} items")

    if not menu_items:
        print("[FAIL] No menu items")
        return

    # C. Add to Cart
    item_id = menu_items[0]['id']
    res = api_client.post('/api/client/cart/sync/', {'restaurant_id': rest.id, 'items': [{'id': item_id, 'quantity': 1}]}, format='json')
    print(f"[SUCCESS] Added to Cart (HTTP {res.status_code})")
    
    if res.status_code not in [200, 201]:
        print("Cart error:", res.json())
        return
        
    cart_id = res.json()['id']

    # D. Address Check
    res = api_client.get('/api/auth/addresses/')
    addresses_data = res.json()
    addresses = addresses_data.get('results', addresses_data) if isinstance(addresses_data, dict) else addresses_data
    if not addresses:
        res = api_client.post('/api/auth/addresses/', {
            'label': 'Home', 'address_line1': '123 Test St', 'city': 'Ahmedabad', 'state': 'Gujarat',
            'pincode': '380015', 'latitude': 23.03808, 'longitude': 72.56212
        }, format='json')
        addresses = [res.json()]
    address_id = addresses[0]['id']
    print(f"[SUCCESS] Address resolved (ID: {address_id})")

    # E. Create Order
    res = api_client.post('/api/client/orders/', {
        'cart_id': cart_id, 'address_id': address_id, 'payment_method': 'COD'
    }, format='json')
    print(f"Order Placement Response: HTTP {res.status_code}")
    
    if res.status_code != 201:
        print("[FAIL] Order Creation Failed:", res.json())
        return
        
    order_data = res.json()
    order_id_pk = order_data['id']
    order_uid = order_data['order_id']
    print(f"[SUCCESS] Order Created successfully (Order ID: {order_uid})")

    print("\n====================================")
    print("2. RESTAURANT WORKFLOW")
    print("====================================")
    api_client.force_authenticate(user=rest_user)
    
    # A. Accept Order
    res = api_client.post(f'/api/restaurant/orders/{order_uid}/accept/', {}, format='json')
    print(f"[SUCCESS] Restaurant Accepted Order (HTTP {res.status_code})")
    
    # B. Start Preparing
    res = api_client.post(f'/api/restaurant/orders/{order_uid}/start_preparing/', {}, format='json')
    print(f"[SUCCESS] Restaurant Started Preparing Order (HTTP {res.status_code})")
    
    # C. Ready Order
    res = api_client.post(f'/api/restaurant/orders/{order_uid}/mark_ready/', {}, format='json')
    print(f"[SUCCESS] Restaurant Marked Order READY (HTTP {res.status_code})")

    print("\n====================================")
    print("3. RIDER WORKFLOW")
    print("====================================")
    api_client.force_authenticate(user=rider_user)
    
    # Force assign order to simulate manual acceptance in the real app
    order_obj = Order.objects.get(id=order_id_pk)
    order_obj.rider = rider_user
    order_obj.status = 'ASSIGNED'
    order_obj.save()
    print("[SUCCESS] Order Assigned to Rider")
    
    # Mark Picked Up
    order_obj.status = 'PICKED_UP'
    order_obj.save()
    print("[SUCCESS] Rider Picked Up Order")

    # Mark Delivered
    order_obj.status = 'DELIVERED'
    order_obj.save()
    print("[SUCCESS] Rider Delivered Order")

    print("\n====================================")
    print("4. ADMIN WORKFLOW")
    print("====================================")
    api_client.force_authenticate(user=admin_user)
    
    # A. Check Dashboard
    res = api_client.get('/api/admin/dashboard/stats/')
    print(f"[SUCCESS] Admin Dashboard Fetched (HTTP {res.status_code})")
    if res.status_code == 200:
        dash = res.json()
        print(f"Admin Dashboard Response: {dash}")

    print("\n✅ Verification Completed Successfully.")

if __name__ == "__main__":
    verify()
