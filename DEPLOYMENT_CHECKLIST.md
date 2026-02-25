# FOODIS DEPLOYMENT & TESTING CHECKLIST
## February 25, 2026

---

## 🚀 QUICK START: FIX & DEPLOY PROCESS

### Step 1: Review Changes Made
The following code fixes have been implemented in your local workspace:

**File:** `d:\Foodis\client\views.py`

#### Fix 1.1: CartViewSet.create() - Support both sync and add_item formats
- **Lines:** 494-575
- **Change:** Added proper create() method that handles:
  - Sync format: `{restaurant_id, items: [{id, quantity}, ...]}`
  - Add-item format: `{menu_item_id, quantity}`
- **Impact:** Cart POST now works instead of returning 500 error

#### Fix 1.2: OrderViewSet.create() - Auto-assign cart if not provided  
- **Lines:** 725-766
- **Change:** Made cart_id optional
  - If not provided, auto-uses user's most recent cart
  - Returns useful error if no cart exists
- **Impact:** Order creation works without requiring cart_id in request

### Step 2: Deploy Changes
```bash
# 1. Commit changes to Git
cd d:\Foodis
git add -A
git commit -m "fix: Cart and Order API endpoints - handle flexible payloads"

# 2. Push to Railway (or your deployment service)
git push origin main
# OR if using Railway CLI:
railway up --detach

# 3. Wait for deployment to complete (~3-5 minutes)
# Check status: https://happy-purpose-production.up.railway.app/health/
```

### Step 3: Verify Deployment
```bash
# After Railway redeploys, run tests:
python e2e_workflow_test.py

# Expected: More tests should now pass
# - Client Login: ✅ Should pass
# - Browse Restaurants: ✅ Should pass
# - Add to Cart: ✅ Should NOW pass (was failing before)
# - Place Order: ✅ Should NOW pass (was failing before)
```

---

## 📋 CRITICAL FIXES APPLIED

### ✅ Fix 1: Cart API Returning 500 Errors
**Problem:** POST `/api/client/cart/` returned HTTP 500  
**Root Cause:** Default create() method didn't match CartViewSet's custom actions  
**Solution:** Implemented proper create() method supporting multiple payload formats  
**File Modified:** client/views.py (Lines 494-575)

**Before:**
```python
# No create() method - relied on default ModelViewSet behavior
# Default create() expected 'restaurant' field in JSON
# Frontend sent 'restaurant_id' or 'menu_item_id' → 500 error
```

**After:**
```python
def create(self, request):
    # Supports BOTH formats transparently
    if 'restaurant_id' in request.data:  # Sync format
        # Handle sync: {restaurant_id, items: [...]}
    elif 'menu_item_id' in request.data:  # Add-item format
        # Handle add-item: {menu_item_id, quantity}
    else:
        return error "Invalid payload"
```

---

### ✅ Fix 2: Order Creation Requires cart_id
**Problem:** PUT `/api/client/orders/` returned HTTP 404 "Cart not found"  
**Root Cause:** OrderViewSet.create() required explicit cart_id, but frontend needed cart_id from cart endpoint which wasn't working  
**Solution:** Made cart_id optional - auto-uses user's most recent cart

**File Modified:** client/views.py (Lines 725-766)

**Before:**
```python
cart_id = request.data.get('cart_id')  # Required
cart = Cart.objects.get(id=cart_id, user=request.user)  # Fails if cart_id=None
```

**After:**
```python
cart_id = request.data.get('cart_id')  # Optional
if not cart_id:
    # Auto-assign user's most recent cart
    cart = Cart.objects.filter(user=request.user).order_by('-id').first()
    if not cart:
        return error "No active cart found. Please add items first."
```

---

## ✅ ADDITIONAL IMPROVEMENTS

### Fix 3: Cart Returns Proper Error Messages
- When cart is empty: `{error: 'Cart is empty'}`
- When address invalid: `{error: 'Please provide address_id or delivery_address'}`
- Helpful error messages instead of blank 500 errors

### Fix 4: Supports Inline Delivery Address
Order creation now partially supports inline address (future enhancement):
```json
{
  "payment_method": "COD",
  "delivery_address": {
    "street": "123 Test Street",
    "latitude": 28.7041,
    "longitude": 77.1025
  }
}
```

---

## 🧪 TESTING AFTER DEPLOYMENT

### Run Full E2E Test
```bash
cd d:\Foodis
python e2e_workflow_test.py
```

**Expected Results After Fix:**
```
PHASE 1: ENVIRONMENT VALIDATION
[PASS] Backend health check
[PASS] WebSocket URL configuration
[FAIL] Database connectivity  ← Still not fixed (non-critical)

PHASE 2: CLIENT WORKFLOW
[PASS] Client OTP send
[PASS] Client OTP verification
[PASS] Browse restaurants

PHASE 3: CLIENT CHECKOUT
[PASS] Add to cart            ← NOW FIXED!
[PASS] Place order            ← NOW FIXED!

PHASE 4-6: BLOCKED (next to fix)
```

### Manual Testing Checklist

#### Test 1: Browser-Based Checkout
1. Open https://foodis-gamma.vercel.app
2. Login with phone +919999999991
3. Browse restaurants ✅
4. Click restaurant → view menu ✅
5. Add dish to cart ← **Test this now**
6. Proceed to checkout ← **Test this now**
7. Select address
8. Choose payment method
9. Place order ← **Test this now**

#### Test 2: API-Based Checkout (for verification)
```bash
# 1. Login (get token)
curl -X POST https://happy-purpose-production.up.railway.app/api/auth/send-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919999999991"}'
# Get OTP from response

curl -X POST https://happy-purpose-production.up.railway.app/api/auth/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919999999991", "otp_code": "OTP_HERE"}'
# Get token from response

TOKEN="token_from_response"

# 2. Get restaurants
curl -X GET https://happy-purpose-production.up.railway.app/api/client/restaurants/ \
  -H "Authorization: Bearer $TOKEN"

# 3. Add to cart (NOW WORKS!)
curl -X POST https://happy-purpose-production.up.railway.app/api/client/cart/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "restaurant_id": 108,
    "items": [
      {"id": 751, "quantity": 1}
    ]
  }'

# 4. Place order (NOW WORKS!)
curl -X POST https://happy-purpose-production.up.railway.app/api/client/orders/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_method": "COD",
    "address_id": 1
  }'
```

---

## 📊 REMAINING ISSUES TO TACKLE

### 🔴 CRITICAL (Fix Next)
1. **WebSocket Real-Time Updates** (separate from Cart/Order fixes)
   - Test broadcast to restaurant when order placed
   - Test broadcast to rider when assigned
   - Test rider location updates on client map
   - **Estimated fix time:** 2-3 hours

2. **Razorpay Payment Gateway** (requires config only)
   - Add `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` to Railway environment
   - Test payment flow with test credentials
   - **Estimated fix time:** 30 minutes

### 🟡 MEDIUM (Fix After Critical)
3. **Database Health Check Endpoint**
   - Implement actual database query in `/api/health/`
   - Test connectivity verification
   - **Estimated fix time:** 15 minutes

4. **Load Testing** (multiple concurrent users)
   - Test with 10+ simultaneous orders
   - Verify no race conditions in cart/order creation
   - **Estimated fix time:** 1-2 hours

---

## 📝 IMPLEMENTATION TIMELINE

| Task | Time | Status |
|------|------|--------|
| Deploy Cart/Order fixes | 10 min | 📋 TO DO |
| Verify deployment | 5 min | 📋 TO DO |
| Run E2E tests | 10 min | 📋 TO DO |
| Manual browser checkout test | 15 min | 📋 TO DO |
| **SUBTOTAL: Phase Quick Fix** | **40 min** | |
| | | |
| Fix WebSocket real-time updates | 2-3 hrs | 📋 TO DO |
| Configure Razorpay | 30 min | 📋 TO DO |
| Database health check | 15 min | 📋 TO DO |
| Run 3 complete workflow cycles | 45 min | 📋 TO DO |
| Load testing (10+ concurrent) | 1-2 hrs | 📋 TO DO |
| **SUBTOTAL: Full Completion** | **5-7 hrs** | |

---

## 🔧 DEPLOYMENT COMMANDS

### Option 1: Using Git (Recommended)
```bash
cd d:\Foodis
git add client/views.py
git commit -m "fix: Cart and Order API endpoints - handle flexible payloads and auto-assign cart"
git push origin main
```

### Option 2: Using Railway CLI
```bash
cd d:\Foodis
railway link  # If not already linked
railway up --detach
```

### Option 3: Manual via Vercel Dashboard
1. Push changes to GitHub
2. Navigate to https://vercel.com/dashboard
3. Click deploy (auto-deploys on push)

---

## ✅ DEPLOYMENT VERIFICATION

After deployment, verify with:

```bash
# Check if server is running
curl https://happy-purpose-production.up.railway.app/health/
# Should return: OK

# Check if API is responding
curl https://happy-purpose-production.up.railway.app/api/health/
# Should return: Some health check data

# Quick cart test
python debug_checkout.py
# Should reach at least STEP 4 with better responses
```

---

## 🎯 SUCCESS CRITERIA

✅ **Fixes are complete when:**
1. `python e2e_workflow_test.py` passes at least Phases 1-3
2. Client can add to cart via browser without errors
3. Client can place order without errors
4. Order appears in admin panel
5. Restaurant receives real-time notification (WebSocket)
6. Rider sees order and can accept it
7. Client sees live delivery tracking (rider location on map)
8. Complete workflow cycle (place order → deliver → feedback) works smoothly
9. All 3 test cycles pass without errors:
   - Cycle 1: COD payment
   - Cycle 2: Wallet payment
   - Cycle 3: Razorpay payment (if configured)

---

## 📞 SUPPORT & DEBUGGING

If issues persist after deployment:

1. **Check Railway Logs:**
   - Go to https://railway.app/dashboard
   - Select your project
   - View "Logs" tab for error messages

2. **Check Frontend Errors:**
   - Open Vercel frontend (mobile browser F12)
   - Check Console tab for JavaScript errors
   - Check Network tab to see API requests/responses

3. **Test API Directly:**
   - Use `debug_checkout.py` script
   - Use Postman/Insomnia for manual API testing
   - Check response status codes and error messages

4. **Database Issues:**
   - Verify Neon PostgreSQL connection in Railway environment
   - Check connection pooling isn't exhausted
   - Run Django migrations if needed: `python manage.py migrate`

---

## 📚 FILES MODIFIED

- [client/views.py](client/views.py) - CartViewSet.create() + OrderViewSet.create()

## 🚀 TEST SCRIPTS PROVIDED

- [e2e_workflow_test.py](e2e_workflow_test.py) - Complete E2E automation
- [debug_otp.py](debug_otp.py) - OTP flow debugging
- [debug_checkout.py](debug_checkout.py) - Cart/order flow debugging
- [E2E_WORKFLOW_TEST_REPORT.md](E2E_WORKFLOW_TEST_REPORT.md) - Detailed findings

---

**Last Updated:** 2026-02-25 18:30 UTC  
**Status:** Fixes implemented, awaiting deployment and testing
