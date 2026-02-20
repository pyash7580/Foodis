import json
import os
import random
import sys
import traceback
import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import django

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodis.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient

from client.models import Category, MenuItem, Order, Restaurant
from core.models import Address, City
from rider_legacy.models import RiderProfile

User = get_user_model()


@dataclass
class StepResult:
    role: str
    workflow: str
    endpoint: str
    method: str
    expected: str
    actual_status: str
    passed: bool
    note: str = ""


class WorkflowTester:
    def __init__(self) -> None:
        self.results: list[StepResult] = []
        self.test_meta: dict[str, Any] = {}
        self.created: dict[str, Any] = {}
        self.clients: dict[str, APIClient] = {}

    def _record(
        self,
        *,
        role: str,
        workflow: str,
        endpoint: str,
        method: str,
        expected_statuses: tuple[int, ...],
        actual_status: int | str,
        note: str = "",
    ) -> None:
        passed = isinstance(actual_status, int) and actual_status in expected_statuses
        self.results.append(
            StepResult(
                role=role,
                workflow=workflow,
                endpoint=endpoint,
                method=method,
                expected="/".join(str(s) for s in expected_statuses),
                actual_status=str(actual_status),
                passed=passed,
                note=note,
            )
        )

    def _extract_json(self, response: Any) -> Any:
        try:
            return response.json()
        except Exception:
            return {}

    def _list_payload(self, payload: Any) -> list[dict]:
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict) and isinstance(payload.get("results"), list):
            return payload["results"]
        return []

    def _call(
        self,
        *,
        client: APIClient,
        role: str,
        workflow: str,
        method: str,
        endpoint: str,
        expected_statuses: tuple[int, ...] = (200,),
        data: dict | None = None,
        note_on_success: str = "",
    ) -> Any:
        try:
            method_l = method.lower()
            if method_l in ("post", "put", "patch"):
                response = getattr(client, method_l)(endpoint, data=data or {}, format="json")
            elif method_l == "delete":
                response = client.delete(endpoint, data=data or {}, format="json")
            else:
                response = client.get(endpoint, data=data or {})

            note = note_on_success
            if response.status_code not in expected_statuses:
                payload = self._extract_json(response)
                note = f"Unexpected response: {json.dumps(payload)[:300]}"

            self._record(
                role=role,
                workflow=workflow,
                endpoint=endpoint,
                method=method.upper(),
                expected_statuses=expected_statuses,
                actual_status=response.status_code,
                note=note,
            )
            return response
        except Exception as exc:
            self._record(
                role=role,
                workflow=workflow,
                endpoint=endpoint,
                method=method.upper(),
                expected_statuses=expected_statuses,
                actual_status="EXCEPTION",
                note=f"{type(exc).__name__}: {exc}",
            )
            return None

    def _phone(self, prefix: str) -> str:
        return f"+91{prefix}{random.randint(10000000, 99999999)}"

    def _authed_client(self, user: User, role_header: str) -> APIClient:
        token = str(RefreshToken.for_user(user).access_token)
        c = APIClient()
        c.credentials(HTTP_AUTHORIZATION=f"Bearer {token}", HTTP_X_ROLE=role_header)
        return c

    def setup_data(self) -> None:
        now_key = datetime.now().strftime("%Y%m%d%H%M%S")
        self.test_meta["run_at"] = timezone.now().isoformat()
        self.test_meta["run_key"] = now_key

        city_mehsana, _ = City.objects.get_or_create(name="Mehsana")
        City.objects.get_or_create(name="Himmatnagar")

        admin_user = User.objects.create_user(
            phone=self._phone("91"),
            name=f"QA Admin {now_key}",
            role="ADMIN",
            is_verified=True,
            password="QaAdmin@123",
            is_staff=True,
            is_superuser=True,
        )
        client_user = User.objects.create_user(
            phone=self._phone("92"),
            name=f"QA Client {now_key}",
            role="CLIENT",
            is_verified=True,
            password="QaClient@123",
        )
        restaurant_user = User.objects.create_user(
            phone=self._phone("93"),
            name=f"QA Restaurant {now_key}",
            role="RESTAURANT",
            is_verified=True,
            password="QaRestaurant@123",
        )
        rider_user = User.objects.create_user(
            phone=self._phone("94"),
            name=f"QA Rider {now_key}",
            role="RIDER",
            is_verified=True,
            password="QaRider@123",
        )

        category = Category.objects.create(name=f"QA Category {now_key}", slug=f"qa-cat-{uuid.uuid4().hex[:8]}")

        restaurant = Restaurant.objects.create(
            owner=restaurant_user,
            name=f"QA Restaurant {now_key}",
            slug=f"qa-restaurant-{uuid.uuid4().hex[:8]}",
            phone=restaurant_user.phone,
            email=f"qa_restaurant_{now_key}@foodis.test",
            address="QA Street 1",
            city="Mehsana",
            city_id=city_mehsana,
            state="Gujarat",
            pincode="384001",
            latitude=Decimal("23.588000"),
            longitude=Decimal("72.369300"),
            status="APPROVED",
            is_active=True,
            min_order_amount=Decimal("0.00"),
            delivery_fee=Decimal("20.00"),
        )

        menu_item = MenuItem.objects.create(
            restaurant=restaurant,
            name=f"QA Dish {now_key}",
            price=Decimal("199.00"),
            category=category,
            is_available=True,
        )

        rider_profile = RiderProfile.objects.create(
            rider=rider_user,
            mobile_number=rider_user.phone,
            city="Mehsana",
            city_id=city_mehsana,
            status="APPROVED",
            onboarding_step=6,
            is_onboarding_complete=True,
            is_online=False,
        )

        address = Address.objects.create(
            user=client_user,
            label="Home",
            address_line1="QA Delivery Point",
            city="Mehsana",
            state="Gujarat",
            pincode="384001",
            latitude=Decimal("23.588100"),
            longitude=Decimal("72.369500"),
            is_default=True,
        )

        self.created.update(
            {
                "city_mehsana": city_mehsana,
                "admin_user": admin_user,
                "client_user": client_user,
                "restaurant_user": restaurant_user,
                "rider_user": rider_user,
                "restaurant": restaurant,
                "menu_item": menu_item,
                "rider_profile": rider_profile,
                "address": address,
            }
        )

        self.clients["public"] = APIClient()
        self.clients["admin"] = self._authed_client(admin_user, "ADMIN")
        self.clients["client"] = self._authed_client(client_user, "CLIENT")
        self.clients["restaurant"] = self._authed_client(restaurant_user, "RESTAURANT")
        self.clients["rider"] = self._authed_client(rider_user, "RIDER")

    def run_common_checks(self) -> None:
        self._call(
            client=self.clients["public"],
            role="COMMON",
            workflow="Health",
            method="get",
            endpoint="/api/health/",
            expected_statuses=(200,),
            note_on_success="Health endpoint reachable",
        )
        self._call(
            client=self.clients["public"],
            role="COMMON",
            workflow="Auth Config",
            method="get",
            endpoint="/api/auth/config/",
            expected_statuses=(200,),
            note_on_success="Auth config endpoint reachable",
        )

        temp_phone = self._phone("95")
        send_resp = self._call(
            client=self.clients["public"],
            role="COMMON",
            workflow="OTP Send",
            method="post",
            endpoint="/api/auth/send-otp/",
            expected_statuses=(200,),
            data={"phone": temp_phone},
        )
        if send_resp is not None and send_resp.status_code == 200:
            otp = self._extract_json(send_resp).get("otp") or "123456"
            self._call(
                client=self.clients["public"],
                role="COMMON",
                workflow="OTP Verify",
                method="post",
                endpoint="/api/auth/verify-otp/",
                expected_statuses=(200,),
                data={"phone": temp_phone, "otp_code": otp, "role": "CLIENT"},
            )

    def run_client_workflow(self) -> None:
        pub = self.clients["public"]
        client = self.clients["client"]

        self._call(
            client=pub,
            role="CLIENT",
            workflow="Browse Restaurants",
            method="get",
            endpoint="/api/client/restaurants/",
            expected_statuses=(200,),
        )
        self._call(
            client=pub,
            role="CLIENT",
            workflow="Browse Menu",
            method="get",
            endpoint=f"/api/client/menu-items/?restaurant={self.created['restaurant'].id}",
            expected_statuses=(200,),
        )
        self._call(
            client=client,
            role="CLIENT",
            workflow="Get Profile",
            method="get",
            endpoint="/api/auth/profile/",
            expected_statuses=(200,),
        )
        self._call(
            client=client,
            role="CLIENT",
            workflow="Get Wallet Balance",
            method="get",
            endpoint="/api/client/wallet/balance/",
            expected_statuses=(200,),
        )
        self._call(
            client=client,
            role="CLIENT",
            workflow="Add Favourite Restaurant",
            method="post",
            endpoint="/api/client/favourite-restaurants/toggle/",
            expected_statuses=(200, 201),
            data={"restaurant_id": self.created["restaurant"].id},
        )
        self._call(
            client=client,
            role="CLIENT",
            workflow="Add Item To Cart",
            method="post",
            endpoint="/api/client/cart/add_item/",
            expected_statuses=(200,),
            data={"menu_item_id": self.created["menu_item"].id, "quantity": 1, "customizations": {}},
        )

        cart_list = self._call(
            client=client,
            role="CLIENT",
            workflow="List Cart",
            method="get",
            endpoint="/api/client/cart/",
            expected_statuses=(200,),
        )

        cart_id = None
        if cart_list is not None and cart_list.status_code == 200:
            carts = self._list_payload(self._extract_json(cart_list))
            if carts:
                cart_id = carts[0].get("id")

        if cart_id:
            order_create = self._call(
                client=client,
                role="CLIENT",
                workflow="Create Order",
                method="post",
                endpoint="/api/client/orders/",
                expected_statuses=(201,),
                data={
                    "cart_id": cart_id,
                    "address_id": self.created["address"].id,
                    "payment_method": "COD",
                    "coupon_code": "",
                    "delivery_instructions": "QA workflow order",
                    "use_wallet": False,
                },
            )
            if order_create is not None and order_create.status_code == 201:
                payload = self._extract_json(order_create)
                order_id = payload.get("order_id")
                if order_id:
                    self.created["order_id"] = order_id
                    order_obj = Order.objects.filter(order_id=order_id).first()
                    if order_obj:
                        self.created["order_pk"] = order_obj.id

                    self._call(
                        client=client,
                        role="CLIENT",
                        workflow="Track Order",
                        method="get",
                        endpoint=f"/api/client/orders/{order_id}/track/",
                        expected_statuses=(200,),
                    )
                    self._call(
                        client=client,
                        role="CLIENT",
                        workflow="List Orders",
                        method="get",
                        endpoint="/api/client/orders/",
                        expected_statuses=(200,),
                    )
        else:
            self._record(
                role="CLIENT",
                workflow="Create Order",
                endpoint="/api/client/orders/",
                method="POST",
                expected_statuses=(201,),
                actual_status="SKIPPED",
                note="No cart_id resolved from cart list response",
            )

    def run_restaurant_workflow(self) -> None:
        restaurant = self.clients["restaurant"]

        self._call(
            client=restaurant,
            role="RESTAURANT",
            workflow="Restaurant Summary",
            method="get",
            endpoint="/api/restaurant/restaurant/summary/",
            expected_statuses=(200,),
        )
        self._call(
            client=restaurant,
            role="RESTAURANT",
            workflow="Restaurant Orders List",
            method="get",
            endpoint="/api/restaurant/orders/",
            expected_statuses=(200,),
        )

        order_id = self.created.get("order_id")
        if not order_id:
            self._record(
                role="RESTAURANT",
                workflow="Order Lifecycle",
                endpoint="/api/restaurant/orders/{order_id}/accept/",
                method="POST",
                expected_statuses=(200,),
                actual_status="SKIPPED",
                note="Client order not created",
            )
            return

        self._call(
            client=restaurant,
            role="RESTAURANT",
            workflow="Accept Order",
            method="post",
            endpoint=f"/api/restaurant/orders/{order_id}/accept/",
            expected_statuses=(200,),
        )
        self._call(
            client=restaurant,
            role="RESTAURANT",
            workflow="Start Preparing",
            method="post",
            endpoint=f"/api/restaurant/orders/{order_id}/start_preparing/",
            expected_statuses=(200,),
        )
        ready_resp = self._call(
            client=restaurant,
            role="RESTAURANT",
            workflow="Mark Ready",
            method="post",
            endpoint=f"/api/restaurant/orders/{order_id}/mark_ready/",
            expected_statuses=(200,),
        )

        pickup_otp = None
        if ready_resp is not None and ready_resp.status_code == 200:
            pickup_otp = self._extract_json(ready_resp).get("pickup_otp")

        if not pickup_otp:
            otp_resp = self._call(
                client=restaurant,
                role="RESTAURANT",
                workflow="Get Pickup OTP",
                method="get",
                endpoint=f"/api/restaurant/orders/{order_id}/get_pickup_otp/",
                expected_statuses=(200,),
            )
            if otp_resp is not None and otp_resp.status_code == 200:
                pickup_otp = self._extract_json(otp_resp).get("pickup_otp")

        if pickup_otp:
            self.created["pickup_otp"] = pickup_otp

    def run_rider_workflow(self) -> None:
        rider = self.clients["rider"]
        profile = self.created["rider_profile"]
        order_pk = self.created.get("order_pk")

        self._call(
            client=rider,
            role="RIDER",
            workflow="Rider Dashboard",
            method="get",
            endpoint="/api/rider/profile/dashboard/",
            expected_statuses=(200,),
        )
        self._call(
            client=rider,
            role="RIDER",
            workflow="Toggle Online",
            method="post",
            endpoint=f"/api/rider/profile/{profile.id}/toggle_online/",
            expected_statuses=(200,),
        )
        self._call(
            client=rider,
            role="RIDER",
            workflow="Available Orders",
            method="get",
            endpoint="/api/rider/orders/available/",
            expected_statuses=(200,),
        )

        if not order_pk:
            self._record(
                role="RIDER",
                workflow="Order Lifecycle",
                endpoint="/api/rider/orders/{id}/accept/",
                method="POST",
                expected_statuses=(200,),
                actual_status="SKIPPED",
                note="Order primary key unavailable",
            )
            return

        self._call(
            client=rider,
            role="RIDER",
            workflow="Accept Order",
            method="post",
            endpoint=f"/api/rider/orders/{order_pk}/accept/",
            expected_statuses=(200,),
        )
        self._call(
            client=rider,
            role="RIDER",
            workflow="Arrived At Restaurant",
            method="post",
            endpoint=f"/api/rider/orders/{order_pk}/arrived_at_restaurant/",
            expected_statuses=(200,),
        )

        pickup_otp = self.created.get("pickup_otp")
        if pickup_otp:
            pickup_resp = self._call(
                client=rider,
                role="RIDER",
                workflow="Pickup Order",
                method="post",
                endpoint=f"/api/rider/orders/{order_pk}/pickup/",
                expected_statuses=(200,),
                data={"otp": pickup_otp},
            )
            if pickup_resp is not None and pickup_resp.status_code == 200:
                self._call(
                    client=rider,
                    role="RIDER",
                    workflow="Start Delivery",
                    method="post",
                    endpoint=f"/api/rider/orders/{order_pk}/start_delivery/",
                    expected_statuses=(200,),
                )
                fresh_order = Order.objects.filter(id=order_pk).first()
                delivery_otp = fresh_order.delivery_otp if fresh_order else None
                if delivery_otp:
                    self._call(
                        client=rider,
                        role="RIDER",
                        workflow="Deliver Order",
                        method="post",
                        endpoint=f"/api/rider/orders/{order_pk}/deliver/",
                        expected_statuses=(200,),
                        data={"otp": delivery_otp},
                    )
                else:
                    self._record(
                        role="RIDER",
                        workflow="Deliver Order",
                        endpoint=f"/api/rider/orders/{order_pk}/deliver/",
                        method="POST",
                        expected_statuses=(200,),
                        actual_status="SKIPPED",
                        note="delivery_otp missing after pickup",
                    )
        else:
            self._record(
                role="RIDER",
                workflow="Pickup Order",
                endpoint=f"/api/rider/orders/{order_pk}/pickup/",
                method="POST",
                expected_statuses=(200,),
                actual_status="SKIPPED",
                note="pickup_otp missing from restaurant workflow",
            )

    def run_admin_workflow(self) -> None:
        admin = self.clients["admin"]

        self._call(
            client=admin,
            role="ADMIN",
            workflow="Dashboard Stats",
            method="get",
            endpoint="/api/admin/dashboard/stats/",
            expected_statuses=(200,),
        )
        self._call(
            client=admin,
            role="ADMIN",
            workflow="Revenue Graph",
            method="get",
            endpoint="/api/admin/dashboard/revenue-graph/",
            expected_statuses=(200,),
        )
        self._call(
            client=admin,
            role="ADMIN",
            workflow="Users List",
            method="get",
            endpoint="/api/admin/users/",
            expected_statuses=(200,),
        )
        self._call(
            client=admin,
            role="ADMIN",
            workflow="Restaurants List",
            method="get",
            endpoint="/api/admin/restaurants/",
            expected_statuses=(200,),
        )
        self._call(
            client=admin,
            role="ADMIN",
            workflow="Riders List",
            method="get",
            endpoint="/api/admin/riders/",
            expected_statuses=(200,),
        )
        self._call(
            client=admin,
            role="ADMIN",
            workflow="Orders List",
            method="get",
            endpoint="/api/admin/orders/",
            expected_statuses=(200,),
        )
        self._call(
            client=admin,
            role="ADMIN",
            workflow="AI Analytics",
            method="get",
            endpoint="/api/admin/analytics/",
            expected_statuses=(200,),
        )
        self._call(
            client=admin,
            role="ADMIN",
            workflow="Fraud Detection",
            method="get",
            endpoint="/api/admin/fraud-detection/",
            expected_statuses=(200,),
        )

    def run_security_checks(self) -> None:
        bad_client = self._authed_client(self.created["client_user"], "RIDER")
        self._call(
            client=bad_client,
            role="SECURITY",
            workflow="Role Header Mismatch",
            method="get",
            endpoint="/api/client/wallet/balance/",
            expected_statuses=(401,),
            note_on_success="Role-aware middleware correctly rejected mismatched role header",
        )

    def write_report(self) -> Path:
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed

        by_role: dict[str, dict[str, int]] = {}
        for row in self.results:
            bucket = by_role.setdefault(row.role, {"total": 0, "passed": 0, "failed": 0})
            bucket["total"] += 1
            if row.passed:
                bucket["passed"] += 1
            else:
                bucket["failed"] += 1

        lines = [
            "# Full System Workflow Test Report",
            "",
            f"- Run timestamp: `{self.test_meta.get('run_at', '')}`",
            f"- Run key: `{self.test_meta.get('run_key', '')}`",
            f"- Total checks: `{total}`",
            f"- Passed: `{passed}`",
            f"- Failed: `{failed}`",
            "",
            "## Role Summary",
            "",
            "| Role | Total | Passed | Failed |",
            "|---|---:|---:|---:|",
        ]
        for role, stats in sorted(by_role.items()):
            lines.append(f"| {role} | {stats['total']} | {stats['passed']} | {stats['failed']} |")

        lines.extend(
            [
                "",
                "## Detailed Results",
                "",
                "| Role | Workflow | Method | Endpoint | Expected | Actual | Result | Note |",
                "|---|---|---|---|---|---|---|---|",
            ]
        )
        for r in self.results:
            result = "PASS" if r.passed else "FAIL"
            safe_note = (r.note or "").replace("|", "/")
            lines.append(
                f"| {r.role} | {r.workflow} | {r.method} | `{r.endpoint}` | {r.expected} | {r.actual_status} | {result} | {safe_note} |"
            )

        lines.extend(
            [
                "",
                "## Test Data",
                "",
                f"- Client user phone: `{self.created['client_user'].phone}`",
                f"- Restaurant owner phone: `{self.created['restaurant_user'].phone}`",
                f"- Rider user phone: `{self.created['rider_user'].phone}`",
                f"- Admin user phone: `{self.created['admin_user'].phone}`",
                f"- Restaurant slug: `{self.created['restaurant'].slug}`",
                f"- Order ID: `{self.created.get('order_id', 'N/A')}`",
                "",
                "## Notes",
                "",
                "- This report validates API workflows and role-based access in backend.",
                "- Frontend behavior is validated via API compatibility, but browser UI interactions were not executed in this script.",
            ]
        )

        report_path = BASE_DIR / "FULL_SYSTEM_TEST_REPORT.md"
        report_path.write_text("\n".join(lines), encoding="utf-8")
        return report_path


def main() -> int:
    tester = WorkflowTester()
    try:
        tester.setup_data()
        tester.run_common_checks()
        tester.run_client_workflow()
        tester.run_restaurant_workflow()
        tester.run_rider_workflow()
        tester.run_admin_workflow()
        tester.run_security_checks()

        report_path = tester.write_report()

        total = len(tester.results)
        passed = sum(1 for r in tester.results if r.passed)
        failed = total - passed

        print("=" * 72)
        print("FULL SYSTEM WORKFLOW TESTING COMPLETE")
        print("=" * 72)
        print(f"Total checks : {total}")
        print(f"Passed       : {passed}")
        print(f"Failed       : {failed}")
        print(f"Report       : {report_path}")
        print("=" * 72)
        return 0 if failed == 0 else 1
    except Exception:
        print("Fatal error while running workflow tests:")
        print(traceback.format_exc())
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
