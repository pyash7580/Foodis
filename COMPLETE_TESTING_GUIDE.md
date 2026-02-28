# FOODIS COMPLETE E2E TESTING & VERIFICATION GUIDE
## A Step-by-Step Guide to Test All Workflows

---

## 📊 TESTING ROADMAP

```
Phase 1: Environment Setup (10 min)
    ↓
Phase 2: Client Login & Browse (15 min)
    ↓
Phase 3: Client Checkout [FIXED] (20 min)
    ↓
Phase 4: Restaurant Accept & Prepare (15 min)
    ↓
Phase 5: Rider Pickup & Delivery (20 min)
    ↓
Phase 6: Admin Dashboard (10 min)
    ↓
Phase 7: Payment & Wallet (10 min)
    ↓
Phase 8: 3x Complete Workflow Cycles (60 min)
    ↓
✅ VERIFICATION COMPLETE
```

**Total Estimated Time:** 160 minutes (~2.5 hours for first full cycle)

---

## PHASE 1: ENVIRONMENT SETUP

### 1.1 Verify Deployment URLs
- Frontend: https://foodis-gamma.vercel.app
- Backend: https://happy-purpose-production.up.railway.app
- WebSocket: wss://happy-purpose-production.up.railway.app/ws

### 1.2 Check Backend Health
```bash
curl https://happy-purpose-production.up.railway.app/health/
# Expected: OK (200 status)

curl https://happy-purpose-production.up.railway.app/api/health/
# Expected: JSON response with status info
```

### 1.3 Prepare Test Accounts
Use these emails for testing (OTP will auto-generate/send via SendGrid):

| Role | Email | Auth Method |
|------|-------|-------------|
| Client 1 | mryash7580@gmail.com | Email OTP |
| Client 2 | test_client_2@example.com | Email OTP |
| Restaurant | test_restaurant@example.com | Email + Password |
| Rider | test_rider@example.com | Email + Password |
| Admin | admin@foodis.com | Email OTP |

Password for all test accounts: `password123`

---

## PHASE 2: CLIENT LOGIN & RESTAURANT BROWSE

### 2.1 Client Login Flow
1. Open http://localhost:3000 in browser
2. Select "Client" login
3. Enter email: `mryash7580@gmail.com`
4. Click "Send OTP"
5. Wait for OTP (Check your real email or console if DEBUG)
6. Enter 6-digit OTP
7. Click "Verify"

**Expected:** Redirects to restaurant list page

### 2.2 Browse Restaurants
1. Verify "Popular Restaurants" section loads
2. Scroll through 50+ restaurants
3. Click one restaurant → view details
4. See menu items with prices

**Expected:** 
- ✅ All images load (from Cloudinary or local storage)
- ✅ Ratings and review count visible
- ✅ Menu categories load properly
- ✅ Item details (price, description, veg/non-veg) show

### 2.3 Verify Restaurant Search
1. Click search icon
2. Type restaurant name
3. Verify results filter

**Expected:** Live search working, results update as you type

---

## PHASE 3: CLIENT CHECKOUT FLOW **[NEWLY FIXED]**

### 3.1 Add Items to Cart
1. From restaurant detail page, click menu item
2. See item details popup
3. Increase quantity to 2
4. Click "Add to Cart"

**Expected:**
- ✅ Cart icon shows item count
- ✅ Item added successfully
- ✅ No error messages
- ✅ Toast/notification shows "Added to cart"

### 3.2 Manage Cart
1. Click cart icon
2. See items in cart with:
   - Restaurant name
   - Individual item prices
   - Quantities
   - Total price

**Actions to test:**
- Increase quantity → Total updates ✅
- Decrease quantity → Total updates ✅
- Remove item → Item disappears ✅
- Continue shopping → Returns to restaurant ✅

### 3.3 Checkout Process
1. Click "Proceed to Checkout"
2. Select delivery address:
   - Choose existing address OR
   - Add new address (street, landmark, coordinates)
3. Select payment method:
   - Cash on Delivery (COD) - default
   - Wallet Payment
   - Online Payment (if Razorpay configured)

**Expected:**
- ✅ Address selection works
- ✅ Payment method selection works
- ✅ Order summary shows correct total

### 3.4 Place Order
1. Click "Place Order"
2. See order confirmation page

**Expected:**
- ✅ Order ID displayed
- ✅ Order details: Items, restaurant, address, total
- ✅ Estimated delivery time shown
- ✅ Order status: "CONFIRMED" or "PENDING"

**API Verification (if using Postman/cURL):**
```bash
# Sync cart
curl -X POST https://happy-purpose-production.up.railway.app/api/client/cart/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "restaurant_id": 108,
    "items": [{"id": 751, "quantity": 2}]
  }'
# Expected: 201 Created, returns cart with items

# Place order
curl -X POST https://happy-purpose-production.up.railway.app/api/client/orders/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_method": "COD",
    "address_id": 1
  }'
# Expected: 201 Created, returns order with ID and status
```

---

## PHASE 4: RESTAURANT ACCEPT & PREPARE

### 4.1 Restaurant Login
1. In separate browser tab/incognito window
2. Go to http://localhost:3000
3. Select "Restaurant" login
4. Enter email: `test_restaurant@example.com`
5. Enter password: `password123`
6. Click "Login"
7. See restaurant dashboard

**Expected:**
- Dashboard loads with restaurant name
- "Pending Orders" section visible
- Order from Phase 3 appears here ✅

### 4.2 Order Notifications [REAL-TIME TEST]
**Check if order appears immediately in restaurant dashboard:**
- If yes ✅ → WebSocket working
- If no, wait 10 seconds and refresh
  - If appears after refresh ⚠️ → WebSocket not working (need polling fallback)
  - If doesn't appear ❌ → Server issue

### 4.3 Accept Order
1. Click pending order
2. See order details:
   - Customer name & phone
   - Delivery address  
   - Items list
   - Total amount
3. Click "Accept Order" button

**Expected:**
- Status changes to "CONFIRMED"
- Order moves to "Active Orders"

### 4.4 Mark as Preparing
1. Click "Start Preparing" button
2. See status change to "PREPARING"

**Expected:**
- ✅ Status updated in UI
- ✅ Timer or timestamp updated
- ✅ OTP generated for rider pickup (6-digit code visible)

### 4.5 Mark Ready for Pickup
1. Click "Ready for Pickup"
2. See status "READY"

**Expected:**
- ✅ Status changes to "READY"
- ✅ Rider assignment triggered automatically OR
- ✅ Manual rider assignment UI appears
- ✅ Client notification sent (visible in their order tracking)

---

## PHASE 5: RIDER PICKUP & DELIVERY

### 5.1 Rider Login
1. Third browser tab/incognito window
2. Go to http://localhost:3000
3. Select "Rider" login
4. Enter email: `test_rider@example.com`
5. Enter password: `password123`
6. Click "Login"
7. See rider dashboard

### 5.2 Go Online
1. Toggle "Go Online" switch
2. Check "Status: Available" ✅

### 5.3 Receive Order Assignment [REAL-TIME TEST]
1. Wait for order to appear in "Available Orders"
   - Should appear after restaurant marks "READY"
   - Check: Does it appear in real-time? (if yes ✅, if requires refresh ⚠️)

2. Click order to accept
3. See:
   - Restaurant location on map
   - Delivery location on map
   - Pickup OTP (6-digit code)

### 5.4 Navigation Test
1. Click "Go to Restaurant"
2. Google Maps opens with directions
3. Arrive at restaurant (simulate by moving map or using "Arrived" button)

### 5.5 Pickup Verification
1. Click "Arrived at Restaurant"
2. Prompt to enter Pickup OTP
3. Enter 6-digit OTP (shown in restaurant dashboard)

**Test:**
- Enter wrong OTP → Error message ❌
- Enter correct OTP → Success ✅

**Expected:**
- Order status: "PICKED_UP"
- Map shows rider en route to delivery location

### 5.6 Delivery Test
1. Status changes to "ON_THE_WAY"
2. Client's order tracking page shows:
   - Rider location on map 🎯
   - "Rider is 2.5 km away" estimate
   - Live location updates as rider moves

**Real-Time Test:** 
- Click rider profile → See latitude/longitude change in real-time ✅
- OR requires page refresh ⚠️
- OR doesn't show rider location ❌

### 5.7 Delivery Completion
1. Rider arrives at customer address
2. Click "Arrived at Customer Location"
3. Prompt to enter Delivery OTP
4. Enter OTP (might be auto-generated or same as pickup)

**Expected:**
- Order status: "DELIVERED"
- Both rider & customer see completion

### 5.8 Verify Payments
- Rider: Sees earnings credit immediately (+50 or configured amount)
- Restaurant: Sees order in earnings section with amount
- Customer: Sees order marked delivered, eligible for refund if COD

---

## PHASE 6: ADMIN DASHBOARD

### 6.1 Admin Login
1. Fourth browser tab
2. Go to http://localhost:3000
3. Select "Admin" login
4. Email: `admin@foodis.com`
5. Pass through OTP or Password flow (as configured)

### 6.2 Orders Tab
1. View all orders across platform
2. Filter by status:
   - Pending
   - Confirmed
   - Preparing
   - Ready
   - Assigned
   - Picked Up
   - On the Way
   - Delivered
   - Cancelled

**Expected:**
- Orders from entire end-to-end flow visible ✅
- Order ID, customer, restaurant, status, payment, amount all shown

### 6.3 Real-Time Order Updates in Admin
While order is being delivered in Rider dashboard:
- Watch admin dashboard
- See status change LIVE as restaurant updates it
- See status change LIVE as rider updates it

**If status changes in real-time:** ✅ WebSocket working  
**If requires page refresh:** ⚠️ WebSocket not working  

### 6.4 Users Tab
1. View all clients, restaurants, riders
2. See test accounts created during workflow

### 6.5 Analytics
1. Check dashboard shows:
   - Total orders (should be ≥1)
   - Revenue (sum of all orders)
   - Active riders
   - Top restaurants

**Expected:** Numbers align with orders created during testing

### 6.6 Restaurant Management
1. View all restaurants
2. See revenue, active menu items, ratings

### 6.7 Rider Management
1. View all riders
2. See status (online/offline), earnings, trips

---

## PHASE 7: PAYMENT TEST

### 7.1 COD Payment Verification
1. Order placed with COD ✅ (already tested)
2. Check payment status: "UNPAID" or "PENDING"
3. After delivery: Check if updates to "PAID" or requires manual settlement

### 7.2 Wallet Payment Test [if configured]
1. Before placing order, go to wallet section
2. Check balance
3. Add money to wallet (if UI allows)
4. Place order with "Wallet" payment
5. Verify balance decreased
6. Check transaction history

### 7.3 Razorpay Payment Test [if keys configured]
1. Place order with "Online Payment" method
2. Razorpay modal opens
3. Complete test payment (use test card: 4111111111111111)
4. Payment verifies
5. Order confirms

**If Razorpay keys not configured:**
- Online payment button disabled ⚠️ or
- Shows error message ⚠️
- **Action:** Add keys to Railway environment and redeploy

---

## PHASE 8: COMPLETE WORKFLOW CYCLES

### Cycle 1: Basic COD Flow
**Time:** ~15 minutes  
**Participants:** 1 Client, 1 Restaurant, 1 Rider (same browser tabs)

```
✅ Client adds item to cart
✅ Client places order (COD)
✅ Restaurant accepts order
✅ Restaurant marks preparing
✅ Restaurant marks ready
✅ Rider accepts order
✅ Rider enters pickup OTP
✅ Rider delivers order
✅ Rider enters delivery OTP
✅ Order status = DELIVERED
✅ Customer sees completion notification
```

### Cycle 2: Wallet Payment + Different Restaurants
**Time:** ~15 minutes  
**Focus:** Test with different restaurant, verify wallet deduction

```
✅ Client adds wallet balance (or uses existing)
✅ Client places order (WALLET method)
✅ Wallet balance decreases
✅ Restaurant accepts & prepares
✅ Rider picks up & delivers
✅ See transaction in wallet history
```

### Cycle 3: Razorpay Payment [if configured]
**Time:** ~15 minutes  
**Focus:** Test online payment flow

```
✅ Client places order (RAZORPAY)
✅ Razorpay modal opens
✅ Test payment completes
✅ Payment verified
✅ Restaurant sees order
✅ Full workflow completes
```

### Success Criteria for All 3 Cycles
- [ ] No errors in browser console
- [ ] No 500 errors in backend
- [ ] Real-time updates working (or polling visible)
- [ ] All statuses transition correctly
- [ ] Payments processed correctly
- [ ] Admin sees all orders
- [ ] Feedback system shows after delivery
- [ ] Earnings reflect correctly for restaurant & rider

---

## 🧪 AUTOMATED TESTING

### Run E2E Test Script
```bash
cd d:\Foodis
python e2e_workflow_test.py
```

**Expected Output:**
```
✓ Backend health check
✓ WebSocket configuration
✓ Client OTP send
✓ Client OTP verify
✓ Browse restaurants
✓ Add to cart [FIXED]
✓ Place order [FIXED]
[Blocked by other fixes...]
```

---

## 🔍 TROUBLESHOOTING GUIDE

### Issue: Order doesn't appear in restaurant view
**Possible Causes:**
1. WebSocket not connected (no real-time notification)
   - Solution: Refresh page, or wait 10sec and refresh
   
2. Order created in database but notification not sent
   - Solution: Check backend logs for errors
   
3. Browser issue
   - Solution: Try incognito window, clear cache

### Issue: Cart POST returns 500
**Status:** FIXED in this update  
**If still occurring:**
1. Check if changes deployed to Railway
2. Verify git push completed
3. Wait 2-3 minutes for Railway to redeploy
4. Force refresh browser (Ctrl+Shift+R)

### Issue: Rider doesn't see order assignment
**Possible Causes:**
1. Rider not marked as online
   - Solution: Toggle "Go Online" switch
   
2. Rider location not in delivery radius
   - Solution: Adjust rider coordinates or radius in admin settings
   
3. Order not marked "READY" by restaurant
   - Solution: Ensure restaurant clicked "Ready for Pickup"

### Issue: Real-time updates not working (statuses don't change until refresh)
**Probable Cause:** WebSocket connection failing  
**Check:**
1. Open browser DevTools → Network → WS tab
2. Look for `wss://happy-purpose-production.up.railway.app/ws` connection
3. If connection shows red/error → WebSocket not connected
4. Check console for errors like "WebSocket connection failed"

**Solution:**
1. Hard refresh page
2. Check Railway logs for Daphne/ASGI errors
3. Verify `ASGI_APPLICATION` set in Django settings
4. May need to investigate WebSocket URL configuration

### Issue: "Cart not found" when placing order
**Status:** FIXED in this update  
**If still occurring:**
1. Verify cart was added (check cart count > 0)
2. Try refreshing cart before checkout
3. Clear browser cache and try again

---

## 📊 PERFORMANCE BENCHMARKS

Target metrics for "Perfect Industry Level":

| Metric | Target | How to Measure |
|--------|--------|---|
| Cart add time | <1s | Time from button click to cart update |
| Order placement time | <2s | Time from "Place Order" to confirmation |
| Real-time notification | <2s | Time from action to notification received |
| Rider location update | <5s | Frequency of map location updates |
| Page load time | <3s | DevTools Network tab |
| API response time | <500ms | Backend logs or Postman |
| Zero 500 errors | 100% | Backend logs check |
| Zero console errors | 100% | Browser DevTools console |

---

## ✅ FINAL VERIFICATION CHECKLIST

Before declaring platform "production ready":

### Functional Requirements
- [ ] Client can login, browse restaurants, add to cart, checkout
- [ ] Restaurant can accept, prepare, and mark ready
- [ ] Rider can accept, pickup, and deliver orders
- [ ] Admin can see all orders and monitor platform
- [ ] Order status flows: PENDING → CONFIRMED → PREPARING → READY → ASSIGNED → PICKED_UP → ON_THE_WAY → DELIVERED
- [ ] OTP verification works for pickup and delivery
- [ ] Payment methods work (COD, Wallet, Razorpay)
- [ ] Feedback/reviews system shows after delivery
- [ ] Earnings calculated correctly for restaurant and rider

### Real-Time Requirements (WebSocket)
- [ ] Restaurant gets real-time notification of new orders
- [ ] Rider gets real-time notification of order assignment
- [ ] Client sees real-time rider location on delivery map
- [ ] Admin sees real-time order status updates
- [ ] All parties see live notifications without page refresh

### Non-Functional Requirements
- [ ] No JavaScript errors in browser console
- [ ] No 500 server errors
- [ ] Page load times < 3 seconds
- [ ] API response times < 500ms
- [ ] Zero data loss or order duplication
- [ ] Secure: No sensitive data in URLs or logs
- [ ] Mobile responsive: Tested on phone (not just desktop)

### Load Testing (Optional but Recommended)
- [ ] 10 concurrent orders placed without errors
- [ ] System remains responsive with 5+ riders online
- [ ] Database connection pool doesn't exhaust
- [ ] No timeout errors under load

---

## 📈 SUCCESS INDICATORS

🎉 **Platform is production-ready when:**
1. All 3 complete workflow cycles pass without errors
2. Real-time updates working (no manual refresh needed)
3. All role workflows functional (client, restaurant, rider, admin)
4. Payment system working
5. Zero crashes or 500 errors
6. Performance benchmarks met
7. All automated tests passing
8. Security considerations addressed

---

**Next Steps:**
1. [START] → Deploy Cart/Order fixes to Railway
2. Run this complete testing guide
3. Document any issues and fix them
4. Repeat until all checkboxes ✅
5. Deploy to production with confidence!

---

*Testing Guide Version 1.0 | Updated 2026-02-25*
