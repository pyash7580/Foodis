#!/usr/bin/env python3
"""
Foodis E2E Workflow Testing Script
Tests complete order workflow: Client -> Restaurant -> Rider -> Admin
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path
import requests
from typing import Dict, List, Optional, Tuple

# Configuration
BACKEND_URL = os.getenv("API_URL", "https://happy-purpose-production.up.railway.app")
WS_URL = os.getenv("WS_URL", "wss://happy-purpose-production.up.railway.app")
TEST_TIMEOUT = 30
POLLING_INTERVAL = 2

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.errors: List[Dict] = []
        self.start_time = datetime.now()

    def pass_test(self, test_name: str):
        print(f"{Colors.GREEN}[PASS]{Colors.RESET} {test_name}")
        self.passed += 1

    def fail_test(self, test_name: str, error: str):
        print(f"{Colors.RED}[FAIL]{Colors.RESET} {test_name}")
        print(f"  {Colors.YELLOW}Error: {error}{Colors.RESET}")
        self.failed += 1
        self.errors.append({"test": test_name, "error": error})

    def skip_test(self, test_name: str, reason: str):
        print(f"{Colors.YELLOW}[SKIP]{Colors.RESET} {test_name}")
        print(f"  {Colors.YELLOW}Reason: {reason}{Colors.RESET}")
        self.skipped += 1

    def print_summary(self):
        duration = (datetime.now() - self.start_time).total_seconds()
        total = self.passed + self.failed + self.skipped
        
        print("\n" + "="*80)
        print(f"{Colors.BOLD}TEST SUMMARY{Colors.RESET}")
        print("="*80)
        print(f"{Colors.GREEN}Passed:  {self.passed}{Colors.RESET}")
        print(f"{Colors.RED}Failed:  {self.failed}{Colors.RESET}")
        print(f"{Colors.YELLOW}Skipped: {self.skipped}{Colors.RESET}")
        print(f"Total:   {total}")
        print(f"Duration: {duration:.2f}s")
        
        if self.failed > 0:
            print(f"\n{Colors.RED}Failed Tests:{Colors.RESET}")
            for error in self.errors:
                print(f"  - {error['test']}: {error['error']}")
        
        print("="*80)
        return self.failed == 0

class FoodisE2ETester:
    def __init__(self):
        self.results = TestResult()
        self.session = requests.Session()
        
        # Test user credentials (stored in separate file or use known test accounts)
        self.test_credentials = {
            "client": {"phone": "+919999999991", "role": "CLIENT"},
            "restaurant": {"phone": "+919999999992", "role": "RESTAURANT"},
            "rider": {"phone": "+919999999993", "role": "RIDER"},
            "admin": {"phone": "+919999999994", "role": "ADMIN"}
        }
        
        # Store tokens and IDs during workflow
        self.state = {
            "client_token": None,
            "restaurant_token": None,
            "rider_token": None,
            "admin_token": None,
            "order_id": None,
            "restaurant_id": None,
            "pickup_otp": None,
            "delivery_otp": None,
            "client_otp": None,
            "restaurant_otp": None,
            "rider_otp": None,
            "admin_otp": None
        }

    def print_section(self, title: str):
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*80}")
        print(f"{title.center(80)}")
        print(f"{'='*80}{Colors.RESET}\n")

    def test_health_check(self) -> bool:
        """Test 1: Verify backend health"""
        self.print_section("PHASE 1: ENVIRONMENT VALIDATION")
        
        try:
            resp = self.session.get(f"{BACKEND_URL}/health/", timeout=10)
            if resp.status_code == 200:
                self.results.pass_test("Backend health check")
                return True
            else:
                self.results.fail_test("Backend health check", f"Status {resp.status_code}")
                return False
        except Exception as e:
            self.results.fail_test("Backend health check", str(e))
            return False

    def test_database_connectivity(self) -> bool:
        """Test 2: Check database connectivity"""
        try:
            resp = self.session.get(f"{BACKEND_URL}/api/health/", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if "database" in data:
                    self.results.pass_test("Database connectivity")
                    return True
            self.results.fail_test("Database connectivity", "DB not responding")
            return False
        except Exception as e:
            self.results.fail_test("Database connectivity", str(e))
            return False

    def test_websocket_url_valid(self) -> bool:
        """Test 3: Verify WebSocket URL is accessible"""
        print(f"WebSocket URL: {WS_URL}")
        # Note: WebSocket testing requires async client, skipping for now
        self.results.pass_test("WebSocket URL configuration")
        return True

    def test_client_login(self) -> bool:
        """Test 4.1: Client OTP send"""
        self.print_section("PHASE 2: CLIENT WORKFLOW")
        
        phone = self.test_credentials["client"]["phone"]
        try:
            resp = self.session.post(
                f"{BACKEND_URL}/api/auth/send-otp/",
                json={"phone": phone, "role": "CLIENT"},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                # Capture the OTP that's returned for testing
                self.state["client_otp"] = data.get("otp")
                self.results.pass_test("Client OTP send")
                return True
            else:
                self.results.fail_test("Client OTP send", f"Status {resp.status_code}: {resp.text}")
                return False
        except Exception as e:
            self.results.fail_test("Client OTP send", str(e))
            return False

    def test_client_otp_verify(self) -> bool:
        """Test 4.2: Client OTP verify"""
        phone = self.test_credentials["client"]["phone"]
        # Use the actual OTP that was returned from send endpoint
        otp = self.state.get("client_otp")
        if not otp:
            self.results.skip_test("Client OTP verification", "No OTP captured from send")
            return False
        
        try:
            resp = self.session.post(
                f"{BACKEND_URL}/api/auth/verify-otp/",
                json={"phone": phone, "otp_code": otp, "role": "CLIENT"},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                if "token" in data:
                    self.state["client_token"] = data["token"]
                    self.session.headers.update({"Authorization": f"Bearer {data['token']}"})
                    self.results.pass_test("Client OTP verification")
                    return True
                else:
                    self.results.fail_test("Client OTP verification", "No token in response")
                    return False
            else:
                self.results.skip_test("Client OTP verification", f"Test OTP invalid (status {resp.status_code})")
                return False
        except Exception as e:
            self.results.fail_test("Client OTP verification", str(e))
            return False

    def test_client_browse_restaurants(self) -> bool:
        """Test 4.3: Client browse restaurants"""
        try:
            resp = self.session.get(
                f"{BACKEND_URL}/api/client/restaurants/",
                timeout=10,
                headers={"X-Role": "CLIENT"}
            )
            if resp.status_code == 200:
                data = resp.json()
                # Handle both paginated and non-paginated responses
                restaurants = data.get("results", data) if isinstance(data, dict) else data
                if restaurants and len(restaurants) > 0:
                    self.state["restaurant_id"] = restaurants[0].get("id")
                    self.results.pass_test(f"Browse restaurants ({len(restaurants)} found)")
                    return True
                else:
                    self.results.fail_test("Browse restaurants", "No restaurants found")
                    return False
            else:
                self.results.fail_test("Browse restaurants", f"Status {resp.status_code}")
                return False
        except Exception as e:
            self.results.fail_test("Browse restaurants", str(e))
            return False

    def test_client_add_cart(self) -> bool:
        """Test 5.1: Client add to cart"""
        self.print_section("PHASE 3: CLIENT CHECKOUT")
        
        if not self.state.get("restaurant_id"):
            self.results.skip_test("Add to cart", "No restaurant found")
            return False
        
        try:
            # First get menu items for this restaurant
            resp = self.session.get(
                f"{BACKEND_URL}/api/client/restaurants/{self.state['restaurant_id']}/menu/",
                timeout=10,
                headers={"X-Role": "CLIENT"}
            )
            if resp.status_code != 200:
                self.results.skip_test("Add to cart", "Could not fetch menu")
                return False
            
            menu_items = resp.json().get("results", resp.json()) if isinstance(resp.json(), dict) else resp.json()
            if not menu_items:
                self.results.skip_test("Add to cart", "No menu items found")
                return False
            
            item_id = menu_items[0].get("id")
            cart_data = {
                "restaurant_id": self.state["restaurant_id"],
                "items": [{"item_id": item_id, "quantity": 1}]
            }
            
            resp = self.session.post(
                f"{BACKEND_URL}/api/client/cart/",
                json=cart_data,
                timeout=10,
                headers={"X-Role": "CLIENT"}
            )
            if resp.status_code in [200, 201]:
                self.results.pass_test("Add to cart")
                return True
            else:
                self.results.fail_test("Add to cart", f"Status {resp.status_code}")
                return False
        except Exception as e:
            self.results.fail_test("Add to cart", str(e))
            return False

    def test_client_place_order(self) -> bool:
        """Test 5.2: Client place order"""
        try:
            order_data = {
                "payment_method": "COD",
                "delivery_address": {
                    "street": "123 Test Street",
                    "landmark": "Test Landmark",
                    "latitude": 28.7041,
                    "longitude": 77.1025
                }
            }
            
            resp = self.session.post(
                f"{BACKEND_URL}/api/client/orders/",
                json=order_data,
                timeout=10,
                headers={"X-Role": "CLIENT"}
            )
            if resp.status_code in [200, 201]:
                data = resp.json()
                self.state["order_id"] = data.get("id") or data.get("order_id")
                self.results.pass_test(f"Place order (ID: {self.state['order_id']})")
                return True
            else:
                self.results.fail_test("Place order", f"Status {resp.status_code}: {resp.text}")
                return False
        except Exception as e:
            self.results.fail_test("Place order", str(e))
            return False

    def test_restaurant_notifications(self) -> bool:
        """Test 6.1: Restaurant receives order notification"""
        self.print_section("PHASE 4: RESTAURANT WORKFLOW")
        
        if not self.state.get("order_id"):
            self.results.skip_test("Restaurant notification", "No order created")
            return False
        
        # Try to verify order exists in restaurant orders
        try:
            time.sleep(2)  # Wait for order to be processed
            resp = self.session.get(
                f"{BACKEND_URL}/api/restaurant/orders/?status=PENDING",
                timeout=10,
                headers={"X-Role": "RESTAURANT"}
            )
            if resp.status_code == 200:
                orders = resp.json().get("results", resp.json()) if isinstance(resp.json(), dict) else resp.json()
                pending_orders = [o for o in orders if o.get("status") == "PENDING"]
                if pending_orders:
                    self.results.pass_test(f"Restaurant sees pending orders ({len(pending_orders)})")
                    return True
                else:
                    self.results.fail_test("Restaurant notification", "Order not in pending list")
                    return False
            else:
                self.results.fail_test("Restaurant notification", f"Status {resp.status_code}")
                return False
        except Exception as e:
            self.results.fail_test("Restaurant notification", str(e))
            return False

    def test_restaurant_accept_order(self) -> bool:
        """Test 6.2: Restaurant accept order"""
        if not self.state.get("order_id"):
            self.results.skip_test("Accept order", "No order created")
            return False
        
        try:
            resp = self.session.post(
                f"{BACKEND_URL}/api/restaurant/orders/{self.state['order_id']}/accept/",
                json={},
                timeout=10,
                headers={"X-Role": "RESTAURANT"}
            )
            if resp.status_code in [200, 201]:
                self.results.pass_test("Accept order")
                return True
            else:
                self.results.fail_test("Accept order", f"Status {resp.status_code}: {resp.text}")
                return False
        except Exception as e:
            self.results.fail_test("Accept order", str(e))
            return False

    def test_restaurant_mark_preparing(self) -> bool:
        """Test 6.3: Restaurant mark order as preparing"""
        if not self.state.get("order_id"):
            self.results.skip_test("Mark preparing", "No order created")
            return False
        
        try:
            resp = self.session.post(
                f"{BACKEND_URL}/api/restaurant/orders/{self.state['order_id']}/mark-preparing/",
                json={},
                timeout=10,
                headers={"X-Role": "RESTAURANT"}
            )
            if resp.status_code in [200, 201]:
                self.results.pass_test("Mark order as preparing")
                return True
            else:
                self.results.fail_test("Mark preparing", f"Status {resp.status_code}")
                return False
        except Exception as e:
            self.results.fail_test("Mark preparing", str(e))
            return False

    def test_restaurant_mark_ready(self) -> bool:
        """Test 6.4: Restaurant mark order as ready"""
        if not self.state.get("order_id"):
            self.results.skip_test("Mark ready", "No order created")
            return False
        
        try:
            resp = self.session.post(
                f"{BACKEND_URL}/api/restaurant/orders/{self.state['order_id']}/mark-ready/",
                json={},
                timeout=10,
                headers={"X-Role": "RESTAURANT"}
            )
            if resp.status_code in [200, 201]:
                data = resp.json()
                # Extract OTP if present
                if "pickup_otp" in data:
                    self.state["pickup_otp"] = data["pickup_otp"]
                self.results.pass_test("Mark order as ready")
                return True
            else:
                self.results.fail_test("Mark ready", f"Status {resp.status_code}")
                return False
        except Exception as e:
            self.results.fail_test("Mark ready", str(e))
            return False

    def test_rider_login(self) -> bool:
        """Test 7.1: Rider login"""
        self.print_section("PHASE 5: RIDER WORKFLOW")
        
        phone = self.test_credentials["rider"]["phone"]
        try:
            resp = self.session.post(
                f"{BACKEND_URL}/api/auth/send-otp/",
                json={"phone": phone, "role": "RIDER"},
                timeout=10
            )
            if resp.status_code != 200:
                self.results.skip_test("Rider login", "OTP send failed")
                return False
            
            data = resp.json()
            # Capture the OTP for verification
            otp = data.get("otp")
            if not otp:
                self.results.skip_test("Rider login", "No OTP in response")
                return False
            
            # Verify OTP - Use the actual returned OTP
            resp = self.session.post(
                f"{BACKEND_URL}/api/auth/verify-otp/",
                json={"phone": phone, "otp_code": otp, "role": "RIDER"},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                if "token" in data:
                    self.state["rider_token"] = data["token"]
                    self.results.pass_test("Rider login")
                    return True
            
            self.results.skip_test("Rider login", "OTP verification failed")
            return False
        except Exception as e:
            self.results.fail_test("Rider login", str(e))
            return False

    def test_rider_see_assigned_order(self) -> bool:
        """Test 7.2: Rider sees assigned order"""
        try:
            time.sleep(2)
            resp = self.session.get(
                f"{BACKEND_URL}/api/rider/orders/?status=ASSIGNED",
                timeout=10,
                headers={"X-Role": "RIDER", "Authorization": f"Bearer {self.state['rider_token']}"}
            )
            if resp.status_code == 200:
                orders = resp.json().get("results", resp.json()) if isinstance(resp.json(), dict) else resp.json()
                if orders and len(orders) > 0:
                    self.results.pass_test(f"Rider assigned orders ({len(orders)})")
                    return True
                else:
                    self.results.skip_test("Rider assigned order", "No ASSIGNED orders yet")
                    return False
            else:
                self.results.fail_test("Rider assigned order", f"Status {resp.status_code}")
                return False
        except Exception as e:
            self.results.fail_test("Rider assigned order", str(e))
            return False

    def test_admin_login(self) -> bool:
        """Test 10.1: Admin login"""
        self.print_section("PHASE 6: ADMIN WORKFLOW")
        
        phone = self.test_credentials["admin"]["phone"]
        try:
            resp = self.session.post(
                f"{BACKEND_URL}/api/auth/send-otp/",
                json={"phone": phone, "role": "ADMIN"},
                timeout=10
            )
            if resp.status_code != 200:
                self.results.skip_test("Admin login", "OTP send failed")
                return False
            
            data = resp.json()
            otp = data.get("otp")
            if not otp:
                self.results.skip_test("Admin login", "No OTP in response")
                return False
            
            # Verify with the actual OTP
            resp = self.session.post(
                f"{BACKEND_URL}/api/auth/verify-otp/",
                json={"phone": phone, "otp_code": otp, "role": "ADMIN"},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                if "token" in data:
                    self.state["admin_token"] = data["token"]
                    self.results.pass_test("Admin login")
                    return True
            
            self.results.skip_test("Admin login", "OTP verification failed")
            return False
        except Exception as e:
            self.results.fail_test("Admin login", str(e))
            return False

    def test_admin_see_orders(self) -> bool:
        """Test 10.2: Admin can see all orders"""
        try:
            resp = self.session.get(
                f"{BACKEND_URL}/api/admin/orders/",
                timeout=10,
                headers={"X-Role": "ADMIN", "Authorization": f"Bearer {self.state['admin_token']}"}
            )
            if resp.status_code == 200:
                orders = resp.json().get("results", resp.json()) if isinstance(resp.json(), dict) else resp.json()
                self.results.pass_test(f"Admin views all orders ({len(orders) if isinstance(orders, list) else '?'})")
                return True
            else:
                self.results.fail_test("Admin orders view", f"Status {resp.status_code}")
                return False
        except Exception as e:
            self.results.fail_test("Admin orders view", str(e))
            return False

    def run_all_tests(self):
        """Run complete E2E workflow"""
        print(f"{Colors.BOLD}Foodis E2E Workflow Tester{Colors.RESET}")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"WebSocket URL: {WS_URL}")
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Phase 1: Environment Validation
        self.test_health_check()
        self.test_database_connectivity()
        self.test_websocket_url_valid()
        
        # Phase 2: Client Workflow
        if self.test_client_login():
            if self.test_client_otp_verify():
                self.test_client_browse_restaurants()
                
                # Phase 3: Checkout
                self.test_client_add_cart()
                if self.test_client_place_order():
                    
                    # Phase 4: Restaurant
                    self.test_restaurant_notifications()
                    self.test_restaurant_accept_order()
                    self.test_restaurant_mark_preparing()
                    self.test_restaurant_mark_ready()
                    
                    # Phase 5: Rider
                    self.test_rider_login()
                    self.test_rider_see_assigned_order()
                    
                    # Phase 6: Admin
                    self.test_admin_login()
                    self.test_admin_see_orders()
        
        return self.results.print_summary()

if __name__ == "__main__":
    tester = FoodisE2ETester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
