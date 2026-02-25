import requests

BASE_URL = "http://127.0.0.1:8000"
# Use the token we got from earlier tests for rider login
# Wait, I need to login as a rider first to get a valid token.
# Let's write the login + test in one script.

def test_available_orders():
    # 1. Login as rider
    login_data = {
        "phone": "+919876543212", # A known rider phone
        "password": "password123",
        "role": "RIDER"
    }
    
    print("Logging in as rider...")
    response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
        
    token = response.json().get('access')
    print(f"Login successful, token obtained.")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Role": "RIDER"
    }
    
    print("Fetching available orders...")
    response = requests.get(f"{BASE_URL}/api/rider/orders/available/", headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        orders = response.json()
        print(f"Returned {len(orders)} available orders.")
        for item in orders:
            print(f"- Order ID: {item.get('order', {}).get('id', 'N/A')}")
            print(f"  Restaurant: {item.get('order', {}).get('restaurant_name', 'N/A')}")
            print(f"  City: {item.get('order', {}).get('city', 'N/A')}")
            print(f"  Distance: {item.get('distance')} km")
            print(f"  Est Earnings: ₹{item.get('estimated_earning')}")
            print("---")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_available_orders()
