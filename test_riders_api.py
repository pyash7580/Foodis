import requests
import json

def fetch_riders():
    try:
        # Login
        res = requests.post('http://127.0.0.1:8001/api/auth/login/', json={'email': '9824949865', 'password': 'admin123'})
        if res.status_code != 200:
            print("Login failed:", res.text)
            return

        token = res.json().get('access')
        
        # Fetch Riders
        headers = {'Authorization': f'Bearer {token}', 'X-Role': 'ADMIN'}
        riders_res = requests.get('http://127.0.0.1:8001/api/admin/riders/', headers=headers)
        
        try:
            data = riders_res.json()
            if isinstance(data, dict) and 'results' in data:
                count = len(data['results'])
                total = data.get('count', 'Unknown')
                print(f"Pagination: Found {count} riders on first page out of {total} total.")
                if count > 0:
                    print(f"First rider: {data['results'][0].get('rider_name', 'Unknown')}")
            elif isinstance(data, list):
                print(f"No pagination: Found {len(data)} riders.")
            else:
                print("Unexpected JSON structure:", list(data.keys())[:5] if isinstance(data, dict) else type(data))
        except json.JSONDecodeError:
            print("Failed to decode JSON:", riders_res.text[:200])
            
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    fetch_riders()
