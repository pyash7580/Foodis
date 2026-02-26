#!/usr/bin/env python3
"""
FOODIS DEPLOYMENT VERIFICATION SCRIPT
Verifies your deployment is working correctly
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from urllib.parse import urljoin

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print(f"{text:^60}")
    print(f"{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.GREEN}[✓] {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.RED}[✗] {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.YELLOW}[!] {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.CYAN}[i] {text}{Colors.ENDC}")

def check_url_exists(url, timeout=10):
    """Check if a URL is responding"""
    try:
        response = requests.get(url, timeout=timeout, allow_redirects=True)
        return response.status_code == 200, response.status_code
    except requests.exceptions.Timeout:
        return False, "Timeout"
    except requests.exceptions.ConnectionError:
        return False, "Connection Error"
    except Exception as e:
        return False, str(e)

def get_backend_url():
    """Get backend URL from environment or user input"""
    # Check environment variable
    backend_url = os.getenv('REACT_APP_API_URL')
    if backend_url:
        return backend_url
    
    # Check frontend/.env.production
    env_file = Path("frontend/.env.production")
    if env_file.exists():
        content = env_file.read_text()
        for line in content.split('\n'):
            if 'REACT_APP_API_URL' in line and '=' in line:
                return line.split('=', 1)[1].strip()
    
    # Ask user
    print(f"{Colors.CYAN}Enter your backend URL (e.g., https://your-domain.railway.app): {Colors.ENDC}", end="")
    return input().strip()

def verify_environment_files():
    """Check if environment files are configured correctly"""
    print_header("Environment Configuration")
    
    env_prod = Path("frontend/.env.production")
    vercel_json = Path("frontend/vercel.json")
    
    checks_passed = True
    
    # Check .env.production
    if env_prod.exists():
        content = env_prod.read_text()
        if 'REACT_APP_API_URL' in content:
            for line in content.split('\n'):
                if 'REACT_APP_API_URL' in line:
                    print_success(f"frontend/.env.production configured: {line}")
                    break
        else:
            print_error("REACT_APP_API_URL not found in .env.production")
            checks_passed = False
    else:
        print_warning("frontend/.env.production not found")
    
    # Check vercel.json
    if vercel_json.exists():
        try:
            with open(vercel_json) as f:
                config = json.load(f)
            print_success("frontend/vercel.json is valid JSON")
        except json.JSONDecodeError as e:
            print_error(f"frontend/vercel.json has invalid JSON: {e}")
            checks_passed = False
    else:
        print_warning("frontend/vercel.json not found")
    
    return checks_passed

def verify_backend_connectivity(backend_url):
    """Check if backend is responding"""
    print_header("Backend Connectivity Check")
    
    if not backend_url:
        print_error("No backend URL provided")
        return False
    
    print_info(f"Testing backend: {backend_url}")
    
    checks = {
        "Health Check": f"{backend_url}/health/",
        "API Root": f"{backend_url}/api/",
        "Restaurants Endpoint": f"{backend_url}/api/client/restaurants/",
    }
    
    all_passed = True
    for name, url in checks.items():
        ok, status = check_url_exists(url)
        if ok:
            print_success(f"{name}: {url}")
        else:
            print_error(f"{name}: {url} (Status: {status})")
            all_passed = False
    
    return all_passed

def verify_frontend_deployment():
    """Check if frontend is deployed and accessible"""
    print_header("Frontend Deployment Check")
    
    frontend_url = "https://foodis-gamma.vercel.app/client"
    print_info(f"Testing frontend: {frontend_url}")
    
    ok, status = check_url_exists(frontend_url)
    if ok:
        print_success(f"Frontend is accessible (Status: {status})")
        return True
    else:
        print_error(f"Frontend not responding (Status: {status})")
        print_warning("This might be because Vercel is still building")
        print_info("Wait a few minutes and try again")
        return False

def test_api_call(backend_url):
    """Test if API calls work from this machine"""
    print_header("API Call Test")
    
    if not backend_url:
        print_warning("Skipping API test - no backend URL")
        return False
    
    headers = {'Content-Type': 'application/json'}
    
    try:
        # Test restaurants endpoint
        url = f"{backend_url}/api/client/restaurants/"
        print_info(f"Testing GET {url}")
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"API responded successfully (Status 200)")
            if isinstance(data, (list, dict)):
                if isinstance(data, dict) and 'results' in data:
                    count = len(data['results'])
                elif isinstance(data, list):
                    count = len(data)
                else:
                    count = "N/A"
                print_info(f"Response contains data: {count} items")
            return True
        else:
            print_warning(f"API returned status {response.status_code}")
            print_info(f"Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print_error("API call timed out")
        return False
    except requests.exceptions.ConnectionError as e:
        print_error(f"Connection error: {e}")
        return False
    except Exception as e:
        print_error(f"Error testing API: {e}")
        return False

def check_git_status():
    """Check if changes are committed"""
    print_header("Git Status")
    
    try:
        result = os.popen('git status --short').read()
        if result.strip():
            print_warning("Uncommitted changes detected:")
            print(result)
            return False
        else:
            print_success("All changes committed")
            return True
    except Exception as e:
        print_warning(f"Could not check git status: {e}")
        return False

def get_deployment_status():
    """Show deployment status"""
    print_header("Deployment Status")
    
    print(f"{Colors.BOLD}Frontend:{Colors.ENDC}")
    print("  URL: https://foodis-gamma.vercel.app/client")
    print("  Status: Check at https://vercel.com/dashboard")
    print("  Last Push: Check git log")
    
    print(f"\n{Colors.BOLD}Backend:{Colors.ENDC}")
    backend_url = get_backend_url()
    if backend_url:
        print(f"  URL: {backend_url}")
        print(f"  Status: Check at respective provider dashboard")
    else:
        print("  Not configured yet")

def run_full_verification():
    """Run complete verification"""
    
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║    FOODIS DEPLOYMENT VERIFICATION TOOL                    ║")
    print("║         Verify Your Production Deployment                 ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(Colors.ENDC)
    
    results = {}
    
    # 1. Check environment files
    results['environment'] = verify_environment_files()
    
    # 2. Get backend URL
    backend_url = get_backend_url()
    print_info(f"Using backend URL: {backend_url}")
    
    # 3. Check git
    results['git'] = check_git_status()
    
    # 4. Check backend
    if backend_url:
        results['backend'] = verify_backend_connectivity(backend_url)
        results['api'] = test_api_call(backend_url)
    
    # 5. Check frontend
    results['frontend'] = verify_frontend_deployment()
    
    # 6. Show status
    get_deployment_status()
    
    # Summary
    print_header("Verification Summary")
    
    checks = [
        ("Environment Configuration", results.get('environment', False)),
        ("Git Status", results.get('git', False)),
        ("Backend Connected", results.get('backend', False)),
        ("API Working", results.get('api', False)),
        ("Frontend Deployed", results.get('frontend', False)),
    ]
    
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    
    for name, result in checks:
        if result:
            print_success(name)
        else:
            print_error(name)
    
    print(f"\n{Colors.BOLD}Overall: {passed}/{total} checks passed{Colors.ENDC}")
    
    if passed == total:
        print_success("✅ Your deployment is ready!")
        return 0
    else:
        print_warning("⚠️ Some checks failed. See above for details.")
        return 1

def main():
    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        return run_full_verification()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Verification cancelled{Colors.ENDC}")
        return 1
    except Exception as e:
        print_error(f"Fatal error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
