
import requests
import json

url = "http://localhost:8000/api/auth/login/"
payload = {
    "email": "nawab-delight@foodis.local",
    "password": "Nawab@"
}

print(f"Testing login for: {payload['email']}")
try:
    response = requests.post(url, json=payload, timeout=5)
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Raw Response: {response.text[:100]}")
except Exception as e:
    print(f"Error: {e}")

# Try with the misspelled one from the screenshot
payload_misspelled = {
    "email": "nawab-delight@foodis.loca",
    "password": "Nawab@"
}
print(f"\nTesting login for (MISSPELLED): {payload_misspelled['email']}")
try:
    response = requests.post(url, json=payload_misspelled, timeout=5)
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Raw Response: {response.text[:100]}")
except Exception as e:
    print(f"Error: {e}")
