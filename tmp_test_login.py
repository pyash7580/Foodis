
import requests

url = "http://localhost:8000/api/auth/login/"
payload = {
    "email": "nawab-delight@foodis.local",
    "password": "Nawab@"
}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

# Try with the misspelled one too
payload_misspelled = {
    "email": "nawab-delight@foodis.loca",
    "password": "Nawab@"
}
try:
    response = requests.post(url, json=payload_misspelled)
    print(f"Misspelled Status Code: {response.status_code}")
    print(f"Misspelled Response Body: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
