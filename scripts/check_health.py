import os
import sys
import subprocess
import socket
import requests
import time
from pathlib import Path

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
BACKEND_LOG = BASE_DIR / "backend_health.log"

def print_status(component, status, detail=""):
    icon = "[PASS]" if status == "OK" else "[FAIL]" if status == "ERROR" else "[WARN]" 
    print(f"{icon:7} {component:25} : {status:10} {detail}")

def check_port(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex((host, port)) == 0

def check_backend():
    print("\n--- Backend Diagnostics ---")
    
    # 1. Environment variables
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        print_status("Environment file (.env)", "OK")
    else:
        print_status("Environment file (.env)", "WARNING", "Not found, using defaults")

    # 2. Django Setup
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')
        import django
        django.setup()
        from django.db import connections
        from django.db.utils import OperationalError
        print_status("Django Environment", "OK")
        
        # 3. Database
        db_conn = connections['default']
        try:
            db_conn.cursor()
            print_status("Database Connection", "OK")
        except OperationalError:
            print_status("Database Connection", "ERROR", "Could not connect to DB")
            
    except Exception as e:
        print_status("Django Environment", "ERROR", str(e))

    # 4. Backend Port
    if check_port('127.0.0.1', 8000):
        print_status("Backend Server (8000)", "OK")
        try:
            res = requests.get("http://127.0.0.1:8000/api/auth/profile/", timeout=2)
            if res.status_code == 401: # Expected if not logged in
                print_status("Backend API Reachability", "OK")
            else:
                print_status("Backend API Reachability", "WARNING", f"Status: {res.status_code}")
        except:
             print_status("Backend API Reachability", "ERROR")
    else:
        print_status("Backend Server (8000)", "ERROR", "Is it running?")

def check_frontend():
    print("\n--- Frontend Diagnostics ---")
    if check_port('127.0.0.1', 3000):
        print_status("Frontend Server (3000)", "OK")
        try:
            res = requests.get("http://127.0.0.1:3000", timeout=2)
            if res.status_code == 200:
                print_status("Frontend Reachability", "OK")
            else:
                print_status("Frontend Reachability", "WARNING", f"Status: {res.status_code}")
        except:
             print_status("Frontend Reachability", "ERROR")
    else:
        print_status("Frontend Server (3000)", "ERROR", "Is it running?")

def check_services():
    print("\n--- Infrastructure ---")
    # Redis
    if check_port('127.0.0.1', 6379):
        print_status("Redis (6379)", "OK")
    else:
        print_status("Redis (6379)", "WARNING", "Required for real-time notifications")

if __name__ == "__main__":
    print("=" * 50)
    print("      FOODIS PROJECT HEALTH CHECK")
    print("=" * 50)
    
    check_backend()
    check_frontend()
    check_services()
    
    print("\n" + "=" * 50)
    print("Recommendation: Run scripts/run_automated_tests.py for full validation.")
    print("=" * 50)
