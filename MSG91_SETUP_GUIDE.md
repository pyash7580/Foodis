# MSG91 SMS OTP Integration Guide

## ✅ SMS OTP is Now Integrated!

Your Foodis app now supports **REAL SMS OTP** sending to actual phone numbers using MSG91.

---

## 🚀 How It Works

1. **With API Key (Production):**
   - Real SMS sent to user's phone number
   - Professional OTP delivery
   - Works with all Indian mobile numbers

2. **Without API Key (Development):**
   - OTP printed to Django console/terminal
   - Perfect for testing
   - No SMS credits needed

---

## 📱 Get FREE MSG91 API Key

### Step 1: Sign Up
1. Go to: **https://msg91.com/signup**
2. Sign up with your email
3. Verify your email address

### Step 2: Get FREE Credits
- MSG91 gives **FREE trial credits**
- Enough for testing (100-500 SMS)
- No credit card required for trial

### Step 3: Get API Credentials
1. Login to MSG91 dashboard
2. Go to **Settings** → **API Keys**
3. Copy your **Auth Key** (API Key)
4. Go to **OTP** section → **Create Template**
5. Create a template like:
   ```
   Your Foodis OTP is ##OTP##. Valid for 5 minutes. Do not share with anyone.
   ```
6. Note the **Template ID**

---

## ⚙️ Configure in Your Project

### Option 1: Add to `.env` file
Open `c:/my/bca/Foodis/.env` and add:

```env
MSG91_API_KEY=your_auth_key_here
MSG91_TEMPLATE_ID=your_template_id_here
```

### Option 2: Test Without SMS (Console Only)
Simply skip adding the API key. OTPs will print to console.

---

## 🔄 Restart Django Server

After adding API keys:
```bash
# Stop current server (Ctrl+C)
# Then restart:
python manage.py runserver
```

---

## ✅ Testing

1. **With MSG91 Configured:**
   - Enter real Indian phone number: `+919876543210`
   - Click "Send OTP"
   - Real SMS delivered to phone
   - Enter OTP from SMS
   - Login successful!

2. **Without MSG91 (Console Mode):**
   - Enter any phone number
   - Click "Send OTP"
   - Check Django terminal/console for OTP
   - Example output:
     ```
     ==================================================
     📱 OTP for +919876543210: 123456
     ==================================================
     ```
   - Enter the OTP shown
   - Login successful!

---

## 🎯 Current Status

✅ SMS OTP integration code added
✅ Auto-fallback to console if no API key
✅ Works with Indian phone numbers (+91)
✅ 6-digit OTP
✅ 5-minute expiry
✅ Secure caching

**Your app works perfectly NOW** - even without MSG91 API key!
Just check the Django console for OTPs during testing.

---

## 💡 Alternative FREE SMS Services

If you prefer other services:

1. **Twilio** - https://www.twilio.com (Free trial $15 credit)
2. **Fast2SMS** - https://www.fast2sms.com (Indian service, free credits)
3. **TextLocal** - https://www.textlocal.in (Free trial)

---

## 📝 Files Modified

1. `core/utils.py` - Added MSG91 integration
2. `foodis/settings.py` - Added MSG91 settings
3. `.env` - Added MSG91 configuration placeholders

---

**Status: ✅ READY TO USE**
Your app sends real OTPs when configured, or prints to console for easy testing!
