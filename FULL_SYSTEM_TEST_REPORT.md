# Full System Workflow Test Report

- Run timestamp: `2026-02-24T14:16:31.519422+00:00`
- Run key: `20260224194631`
- Total checks: `36`
- Passed: `36`
- Failed: `0`

## Role Summary

| Role | Total | Passed | Failed |
|---|---:|---:|---:|
| ADMIN | 8 | 8 | 0 |
| CLIENT | 10 | 10 | 0 |
| COMMON | 4 | 4 | 0 |
| RESTAURANT | 5 | 5 | 0 |
| RIDER | 8 | 8 | 0 |
| SECURITY | 1 | 1 | 0 |

## Detailed Results

| Role | Workflow | Method | Endpoint | Expected | Actual | Result | Note |
|---|---|---|---|---|---|---|---|
| COMMON | Health | GET | `/api/health/` | 200 | 200 | PASS | Health endpoint reachable |
| COMMON | Auth Config | GET | `/api/auth/config/` | 200 | 200 | PASS | Auth config endpoint reachable |
| COMMON | OTP Send | POST | `/api/auth/send-otp/` | 200 | 200 | PASS |  |
| COMMON | OTP Verify | POST | `/api/auth/verify-otp/` | 200 | 200 | PASS |  |
| CLIENT | Browse Restaurants | GET | `/api/client/restaurants/` | 200 | 200 | PASS |  |
| CLIENT | Browse Menu | GET | `/api/client/menu-items/?restaurant=108` | 200 | 200 | PASS |  |
| CLIENT | Get Profile | GET | `/api/auth/profile/` | 200 | 200 | PASS |  |
| CLIENT | Get Wallet Balance | GET | `/api/client/wallet/balance/` | 200 | 200 | PASS |  |
| CLIENT | Add Favourite Restaurant | POST | `/api/client/favourite-restaurants/toggle/` | 200/201 | 201 | PASS |  |
| CLIENT | Add Item To Cart | POST | `/api/client/cart/add_item/` | 200 | 200 | PASS |  |
| CLIENT | List Cart | GET | `/api/client/cart/` | 200 | 200 | PASS |  |
| CLIENT | Create Order | POST | `/api/client/orders/` | 201 | 201 | PASS |  |
| CLIENT | Track Order | GET | `/api/client/orders/ORDC5C41A7D9D/track/` | 200 | 200 | PASS |  |
| CLIENT | List Orders | GET | `/api/client/orders/` | 200 | 200 | PASS |  |
| RESTAURANT | Restaurant Summary | GET | `/api/restaurant/restaurant/summary/` | 200 | 200 | PASS |  |
| RESTAURANT | Restaurant Orders List | GET | `/api/restaurant/orders/` | 200 | 200 | PASS |  |
| RESTAURANT | Accept Order | POST | `/api/restaurant/orders/ORDC5C41A7D9D/accept/` | 200 | 200 | PASS |  |
| RESTAURANT | Start Preparing | POST | `/api/restaurant/orders/ORDC5C41A7D9D/start_preparing/` | 200 | 200 | PASS |  |
| RESTAURANT | Mark Ready | POST | `/api/restaurant/orders/ORDC5C41A7D9D/mark_ready/` | 200 | 200 | PASS |  |
| RIDER | Rider Dashboard | GET | `/api/rider/profile/dashboard/` | 200 | 200 | PASS |  |
| RIDER | Toggle Online | POST | `/api/rider/profile/4/toggle_online/` | 200 | 200 | PASS |  |
| RIDER | Available Orders | GET | `/api/rider/orders/available/` | 200 | 200 | PASS |  |
| RIDER | Accept Order | POST | `/api/rider/orders/3/accept/` | 200 | 200 | PASS |  |
| RIDER | Arrived At Restaurant | POST | `/api/rider/orders/3/arrived_at_restaurant/` | 200 | 200 | PASS |  |
| RIDER | Pickup Order | POST | `/api/rider/orders/3/pickup/` | 200 | 200 | PASS |  |
| RIDER | Start Delivery | POST | `/api/rider/orders/3/start_delivery/` | 200 | 200 | PASS |  |
| RIDER | Deliver Order | POST | `/api/rider/orders/3/deliver/` | 200 | 200 | PASS |  |
| ADMIN | Dashboard Stats | GET | `/api/admin/dashboard/stats/` | 200 | 200 | PASS |  |
| ADMIN | Revenue Graph | GET | `/api/admin/dashboard/revenue-graph/` | 200 | 200 | PASS |  |
| ADMIN | Users List | GET | `/api/admin/users/` | 200 | 200 | PASS |  |
| ADMIN | Restaurants List | GET | `/api/admin/restaurants/` | 200 | 200 | PASS |  |
| ADMIN | Riders List | GET | `/api/admin/riders/` | 200 | 200 | PASS |  |
| ADMIN | Orders List | GET | `/api/admin/orders/` | 200 | 200 | PASS |  |
| ADMIN | AI Analytics | GET | `/api/admin/analytics/` | 200 | 200 | PASS |  |
| ADMIN | Fraud Detection | GET | `/api/admin/fraud-detection/` | 200 | 200 | PASS |  |
| SECURITY | Role Header Mismatch | GET | `/api/client/wallet/balance/` | 401 | 401 | PASS | Role-aware middleware correctly rejected mismatched role header |

## Test Data

- Client user phone: `+919265725560`
- Restaurant owner phone: `+919360572209`
- Rider user phone: `+919459056061`
- Admin user phone: `+919153498800`
- Restaurant slug: `qa-restaurant-644fd1b2`
- Order ID: `ORDC5C41A7D9D`

## Notes

- This report validates API workflows and role-based access in backend.
- Frontend behavior is validated via API compatibility, but browser UI interactions were not executed in this script.