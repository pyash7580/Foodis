#!/usr/bin/env python3
"""
Verify Vercel Deployment is Working
Tests frontend, backend, and API connectivity
"""

import sys
import time
try:
    import requests
except ImportError:
    print("Installing requests...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "requests"], check=True)
    import requests

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def test_url(url, name, timeout=10):
    """Test if URL is reachable"""
    try:
        response = requests.get(url, timeout=timeout, allow_redirects=True)
        status = response.status_code
        if status in [200, 301, 302]:
            print(f"{GREEN}✅ {name}{RESET}")
            print(f"   Status: {status}")
            return True
        else:
            print(f"{YELLOW}⚠️  {name}{RESET}")
            print(f"   Status: {status}")
            return False
    except requests.exceptions.Timeout:
        print(f"{YELLOW}⏳ {name}{RESET}")
        print(f"   Timeout (service may be sleeping)")
        return False
    except Exception as e:
        print(f"{RED}❌ {name}{RESET}")
        print(f"   Error: {str(e)[:50]}...")
        return False

def main():
    print(f"""
{BLUE}╔════════════════════════════════════════════════════════════╗
║        VERCEL DEPLOYMENT VERIFICATION TEST                  ║
║                                                              ║
║  This will test:                                            ║
║  1. Frontend is live on Vercel                              ║
║  2. Backend is deployed on Render                           ║
║  3. Communication is working                                ║
╚════════════════════════════════════════════════════════════╝{RESET}
""")

    print(f"\n{BLUE}ENTER YOUR DEPLOYMENT URLS:{RESET}\n")
    
    frontend_url = input("Frontend URL (default: https://foodis-gamma.vercel.app/client): ").strip()
    if not frontend_url:
        frontend_url = "https://foodis-gamma.vercel.app/client"
    
    backend_url = input("Backend URL (e.g., https://foodis-backend-xxxxx.onrender.com): ").strip()
    if not backend_url:
        print(f"{RED}Backend URL is required!{RESET}")
        sys.exit(1)
    
    if not backend_url.startswith("https://"):
        backend_url = "https://" + backend_url

    print(f"\n{BLUE}TESTING DEPLOYMENT:{RESET}\n")

    # Test frontend
    print(f"1. Testing Frontend...")
    print(f"   URL: {frontend_url}")
    frontend_ok = test_url(frontend_url, "Frontend is live")

    # Test backend
    print(f"\n2. Testing Backend...")
    print(f"   URL: {backend_url}")
    backend_ok = test_url(backend_url, "Backend is running")

    # Test API endpoint
    print(f"\n3. Testing API Endpoint...")
    api_url = f"{backend_url}/api/client/restaurants/"
    print(f"   URL: {api_url}")
    api_ok = test_url(api_url, "API endpoint responds")

    # Test health endpoint
    print(f"\n4. Testing Health Check...")
    health_url = f"{backend_url}/health/"
    print(f"   URL: {health_url}")
    health_ok = test_url(health_url, "Health check endpoint", timeout=5)

    # Summary
    print(f"\n{BLUE}═" * 60)
    print(f"DEPLOYMENT STATUS SUMMARY{RESET}\n")

    tests = [
        ("Frontend Live", frontend_ok),
        ("Backend Running", backend_ok),
        ("API Responding", api_ok),
        ("Health Check", health_ok),
    ]

    passed = sum(1 for _, ok in tests if ok)
    total = len(tests)

    for name, ok in tests:
        symbol = f"{GREEN}✅{RESET}" if ok else f"{RED}❌{RESET}"
        print(f"{symbol} {name}")

    print(f"\n{BLUE}Total: {passed}/{total} tests passed{RESET}")

    if passed == total:
        print(f"\n{GREEN}🎉 ALL TESTS PASSED! Your deployment is working!{RESET}\n")
        print("Next steps:")
        print("1. Visit your frontend URL")
        print("2. Test login (OTP: 000000)")
        print("3. Browse restaurants")
        print("4. Add to cart and checkout")
        print("\nEnjoy your live app! 🚀")
        return 0
    
    elif passed >= 3:
        print(f"\n{YELLOW}⚠️  Some tests failed, but basics are working{RESET}\n")
        print("Troubleshooting tips:")
        if not frontend_ok:
            print("❌ Frontend issue:")
            print("   - Check URL is correct")
            print("   - Hard refresh: Ctrl+Shift+R")
            print("   - Check Vercel deployment logs")
        if not backend_ok:
            print("❌ Backend issue:")
            print("   - Service may still be deploying (5-10 min)")
            print("   - Check Render logs")
            print("   - Verify DATABASE_URL is set correctly")
        if not api_ok:
            print("❌ API issue:")
            print("   - Same as backend issue above")
            print("   - Or check CORS settings in Django")
        return 1
    
    else:
        print(f"\n{RED}❌ MAJOR ISSUES - Deployment not working{RESET}\n")
        print("Critical steps to check:")
        print("1. Is backend URL correct?")
        print("2. Is Render deployment showing 'Live' status?")
        print("3. Is Vercel showing 'Production' deployment?")
        print("4. Wait 2-3 more minutes (services may be starting)")
        print("\nThen run this test again.")
        return 2

    print()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Test interrupted{RESET}")
        sys.exit(1)
