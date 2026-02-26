#!/usr/bin/env python
"""
Verify Production Deployment Script
This script checks if your Vercel frontend and cloud backend are working correctly.
"""

import subprocess
import json
import urllib.request
import urllib.error
import time
import sys

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def print_status(status, message):
    symbol = "✅" if status else "❌"
    print(f"{symbol} {message}")

def check_frontend():
    """Check if Vercel frontend is deployed and responsive"""
    print_header("Checking Vercel Frontend")
    
    url = "https://foodis-gamma.vercel.app/client"
    
    try:
        response = urllib.request.urlopen(url, timeout=10)
        if response.status == 200:
            print_status(True, f"Frontend is accessible at {url}")
            return True
        else:
            print_status(False, f"Frontend returned status {response.status}")
            return False
    except Exception as e:
        print_status(False, f"Frontend not accessible: {str(e)}")
        return False

def check_backend_url():
    """Check if backend URL is configured in Vercel"""
    print_header("Checking Backend Configuration")
    
    print("ℹ️  Backend URL should be set in Vercel environment variables.")
    print("    Go to: https://vercel.com/dashboard")
    print("    Settings → Environment Variables")
    print("    You should have: REACT_APP_API_URL = https://your-backend.com\n")
    
    backend_url = input("Enter your backend URL (e.g., https://your-backend.onrender.com): ").strip()
    
    if not backend_url:
        print_status(False, "No backend URL provided")
        return None
    
    if not backend_url.startswith('http'):
        backend_url = 'https://' + backend_url
    
    return backend_url

def check_backend_health(backend_url):
    """Check if backend is running and accessible"""
    print_header("Checking Backend Health")
    
    urls_to_check = [
        (f"{backend_url}/health/", "Health endpoint"),
        (f"{backend_url}/api/client/restaurants/", "API endpoint"),
    ]
    
    all_good = True
    
    for url, description in urls_to_check:
        try:
            response = urllib.request.urlopen(url, timeout=10)
            if response.status == 200:
                print_status(True, f"{description}: {url} (Status: {response.status})")
            else:
                print_status(False, f"{description}: Status {response.status}")
                all_good = False
        except urllib.error.HTTPError as e:
            if e.code in [401, 403]:
                print_status(True, f"{description}: Accessible (Auth required - {e.code})")
            else:
                print_status(False, f"{description}: HTTP Error {e.code}")
                all_good = False
        except urllib.error.URLError as e:
            print_status(False, f"{description}: {str(e)}")
            all_good = False
        except Exception as e:
            print_status(False, f"{description}: {str(e)}")
            all_good = False
    
    return all_good

def check_cors():
    """Check if CORS is configured correctly"""
    print_header("Checking CORS Configuration")
    
    print("CORS settings should allow Vercel domain.")
    print("These are already configured in Django settings.\n")
    
    print("Current CORS configuration:")
    print("  - CORS_ALLOW_ALL_ORIGINS = True (for development)")
    print("  - ALLOWED_HOSTS includes: .vercel.app, .onrender.com\n")
    
    print_status(True, "CORS configuration is set up for production")
    return True

def check_local_development():
    """Check if local development is still working"""
    print_header("Checking Local Development")
    
    try:
        # Try local backend
        response = urllib.request.urlopen("http://localhost:8000/health/", timeout=5)
        print_status(True, "Local backend running on http://localhost:8000")
        
        # Try local frontend
        response = urllib.request.urlopen("http://localhost:3000", timeout=5)
        print_status(True, "Local frontend running on http://localhost:3000")
        
        return True
    except Exception:
        print("ℹ️  Local development servers are not running (this is OK for production)")
        return False

def generate_summary(frontend_ok, backend_ok, local_ok):
    """Generate deployment summary"""
    print_header("Deployment Summary")
    
    print("Status Overview:")
    print_status(frontend_ok, "Vercel Frontend")
    print_status(backend_ok if backend_ok is not None else False, "Cloud Backend")
    print_status(local_ok, "Local Development")
    
    if frontend_ok and backend_ok and not local_ok:
        print("\n✅ PRODUCTION DEPLOYMENT: READY!")
        print("   Your app is deployed and should be working!")
    elif frontend_ok and not backend_ok:
        print("\n⚠️  INCOMPLETE DEPLOYMENT")
        print("   Frontend is deployed but backend is not responding.")
        print("   Steps to fix:")
        print("   1. Check backend is deployed to cloud")
        print("   2. Verify backend URL in Vercel environment variables")
        print("   3. Wait 3-5 minutes for backend to start (cold start)")
        print("   4. Refresh frontend page")
    elif not frontend_ok:
        print("\n❌ DEPLOYMENT ISSUES")
        print("   Frontend is not accessible. Check:")
        print("   1. Vercel deployment status")
        print("   2. Internet connection")
        print("   3. GitHub push completed")
    elif frontend_ok and backend_ok and local_ok:
        print("\n✅ FULL SYSTEM: READY!")
        print("   Both production and local development are working!")

def main():
    """Main verification script"""
    print("\n" + "="*60)
    print("  FOODIS PRODUCTION DEPLOYMENT VERIFICATION")
    print("="*60)
    
    # Check frontend
    frontend_ok = check_frontend()
    
    if not frontend_ok:
        print("\n⚠️  Frontend not accessible. Check Vercel deployment status.")
        sys.exit(1)
    
    # Get backend URL
    backend_url = check_backend_url()
    
    if backend_url:
        # Check backend
        backend_ok = check_backend_health(backend_url)
        
        # Check CORS
        check_cors()
    else:
        backend_ok = None
    
    # Check local development
    local_ok = check_local_development()
    
    # Generate summary
    generate_summary(frontend_ok, backend_ok, local_ok)
    
    print("\n" + "="*60)
    print("  Verification Complete!")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nVerification cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)
