import urllib.request
import sys

frontend_url = "https://foodis-gamma.vercel.app"

print(f"Pinging Vercel Frontend: {frontend_url}")

try:
    req = urllib.request.Request(frontend_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as response:
        if response.getcode() == 200:
            print("\n[OK] Vercel Frontend is up and running!")
            sys.exit(0)
        else:
             print(f"\n[FAIL] Vercel Frontend returned {response.getcode()}")
             sys.exit(1)
except Exception as e:
    print(f"\n[FAIL] Error accessing frontend: {e}")
    sys.exit(1)
