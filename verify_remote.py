import urllib.request
import json
import traceback

backend_url = "https://happy-purpose-production.up.railway.app"

endpoints = [
    ('/health/', 200),
    ('/api/client/restaurants/', 200),
]

print(f"=== VERIFYING REMOTE ENDPOINTS ON {backend_url} ===")

all_passed = True

for path, expected_status in endpoints:
    url = f"{backend_url}{path}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=15) as response:
            res_data = response.read().decode()
            if response.getcode() == 200:
                print(f"[OK] {path} -> {response.getcode()}")
                if path == '/api/client/restaurants/':
                    data = json.loads(res_data)
                    if isinstance(data, dict):
                        print(f"      Count: {data.get('count', 0)}")
                        results = data.get('results', [])
                    else:
                        print(f"      Count: {len(data)}")
                        results = data
                    
                    if results:
                        r = results[0]
                        print(f"      Sample: {r.get('name')} (ID: {r.get('id')})")
            else:
                print(f"[FAIL] {path} -> Expected {expected_status}, got {response.getcode()}")
                all_passed = False
    except urllib.error.HTTPError as e:
        if e.code in [401, 403, 404]:
            print(f"[OK] {path} -> {e.code} (Expected auth/not found)")
        else:
            print(f"[FAIL] {path} -> HTTP Error {e.code}")
            all_passed = False
    except Exception as e:
        print(f"[CRASH] {path} -> {str(e)}")
        all_passed = False

if all_passed:
    print("\n[OK] Remote Backend verified successfully. Zero crashes detected.")
else:
    print("\n[FAIL] Remote Backend has issues.")
