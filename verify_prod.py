import urllib.request
import time
import sys

backend_url = "https://happy-purpose-production.up.railway.app/health/"
timeout_mins = 5
end_time = time.time() + (timeout_mins * 60)

print(f"Waiting for Railway backend to be healthy at {backend_url}...")

while time.time() < end_time:
    try:
        req = urllib.request.Request(backend_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.getcode() == 200:
                print("\n[OK] Railway Backend is live and healthy!")
                sys.exit(0)
    except Exception as e:
        print(".", end="", flush=True)
    time.sleep(10)

print("\n[FAIL] Timeout waiting for backend to become healthy. It might be crashing on startup.")
sys.exit(1)
