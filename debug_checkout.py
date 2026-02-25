#!/usr/bin/env python3
import requests
import json

BACKEND_URL = "https://happy-purpose-production.up.railway.app"

print("="*80)
print("FOODIS CHECKOUT FLOW DEBUG")
print("="*80)

# Step 1: Client Login
print("\n[STEP 1] Client Login...")
phone = "+919999999991"
resp = requests.post(f"{BACKEND_URL}/api/auth/send-otp/", json={"phone": phone, "role": "CLIENT"})
otp = resp.json().get("otp")
print(f"OTP: {otp}")

resp = requests.post(f"{BACKEND_URL}/api/auth/verify-otp/", json={"phone": phone, "otp_code": otp})
token = resp.json().get("token")
print(f"Token: {token[:50]}...")

headers = {"Authorization": f"Bearer {token}", "X-Role": "CLIENT"}

# Step 2: Get restaurants
print("\n[STEP 2] Get restaurants...")
resp = requests.get(f"{BACKEND_URL}/api/client/restaurants/", headers=headers)
print(f"Response status: {resp.status_code}")
resp_data = resp.json()
# Handle both list and paginated responses
if isinstance(resp_data, list):
    restaurants = resp_data
elif isinstance(resp_data, dict) and "results" in resp_data:
    restaurants = resp_data["results"]
else:
    restaurants = resp_data
print(f"Got {len(restaurants) if isinstance(restaurants, list) else '?'} restaurants")
if isinstance(restaurants, list) and restaurants:
    restaurant_id = restaurants[0]["id"]
    print(f"Using restaurant {restaurant_id}")
else:
    print(f"Could not get restaurants. Response: {json.dumps(restaurants, indent=2)[:500]}")
    exit(1)

# Step 3: Get menu for restaurant
print(f"\n[STEP 3] Get menu for restaurant {restaurant_id}...")
resp = requests.get(f"{BACKEND_URL}/api/client/restaurants/{restaurant_id}/menu/", headers=headers)
print(f"Status: {resp.status_code}")
try:
    menu = resp.json()
    print(f"Response: {json.dumps(menu, indent=2)[:500]}...")
except Exception as e:
    print(f"Error parsing response: {e}")
    print(f"Raw response: {resp.text[:500]}")

# Step 4: Try different cart endpoints
print("\n[STEP 4] Testing cart endpoints...")

menu_item_id = None
if isinstance(menu, list) and menu:
    menu_item_id = menu[0]["id"]
    print(f"Found menu item ID: {menu_item_id}")

cart_endpoints = [
    ("Sync cart format", "POST", f"{BACKEND_URL}/api/client/cart/", {"restaurant_id": restaurant_id, "items": [{"id": menu_item_id, "quantity": 1}]} if menu_item_id else None),
    ("Add item format", "POST", f"{BACKEND_URL}/api/client/cart/", {"menu_item_id": menu_item_id, "quantity": 1} if menu_item_id else None),
    ("GET /cart/", "GET", f"{BACKEND_URL}/api/client/cart/", None),
]

for i, (desc, method, url, data) in enumerate(cart_endpoints, 1):
    if data is None and method == "POST":
        print(f"\n  {i}. {desc}... SKIPPED (no menu item found)")
        continue
    print(f"\n  {i}. {desc}...")
    try:
        if method == "POST":
            resp = requests.post(url, json=data, headers=headers, timeout=10)
        else:
            resp = requests.get(url, headers=headers, timeout=10)
        print(f"    Status: {resp.status_code}")
        try:
            print(f"    Response: {json.dumps(resp.json(), indent=2)[:500]}...")
        except:
            print(f"    Response: {resp.text[:500]}")
    except Exception as e:
        print(f"    Error: {e}")

# Step 5: Try order creation
print("\n[STEP 5] Testing order creation...")
resp = requests.post(
    f"{BACKEND_URL}/api/client/orders/",
    json={
        "payment_method": "COD",
        "delivery_address": {
            "street": "Test Street",
            "landmark": "Test Landmark",
            "latitude": 28.7041,
            "longitude": 77.1025
        }
    },
    headers=headers
)
print(f"Status: {resp.status_code}")
try:
    print(f"Response: {json.dumps(resp.json(), indent=2)}")
except:
    print(f"Response: {resp.text}")
