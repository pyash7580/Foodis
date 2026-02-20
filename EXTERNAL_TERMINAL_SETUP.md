# Foodis Project - External Terminal Setup Guide
# ===========================================

## 🚀 Quick Start with External Terminal

### 1. Open External Terminal
- **Windows**: Open Command Prompt (cmd) or PowerShell
- **Shortcut**: `Win + R` → type `cmd` or `powershell`

### 2. Navigate to Project Directory
```bash
cd c:\my\bca\Foodis
```

### 3. Start Django Server

#### Option A: Use PowerShell Script (Recommended)
```powershell
# In PowerShell
powershell -ExecutionPolicy Bypass -File "run_server.ps1"
```

#### Option B: Use Batch File
```batch
# In Command Prompt (cmd)
run_server.bat
```

#### Option C: Direct Python Command
```bash
# In any terminal
.venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
```

### 4. Start Frontend (Separate Terminal)
```bash
# Open new terminal, then:
cd c:\my\bca\Foodis\frontend
npm start
```

## 🌐 Access Points
- **Backend API**: http://localhost:8000
- **Frontend App**: http://localhost:3000
- **Admin Panel**: http://localhost:8000/admin/

## 📱 Testing OTP in External Terminal

### Send OTP via API
```powershell
# PowerShell
Invoke-RestMethod -Uri "http://localhost:8000/api/auth/send-otp/" -Method POST -ContentType "application/json" -Body '{"phone": "+1234567890"}'

# Command Prompt
curl -X POST http://localhost:8000/api/auth/send-otp/ -H "Content-Type: application/json" -d "{\"phone\": \"+1234567890\"}"
```

### Find OTP with Helper Script
```bash
python find_otp.py --phone "+1234567890"
```

## 🔧 Virtual Environment
Always use the virtual environment Python:
```bash
# Activate (if needed)
.venv\Scripts\activate

# Or use full path
.venv\Scripts\python.exe manage.py <command>
```

## 📝 Useful Commands
```bash
# Database migrations
.venv\Scripts\python.exe manage.py migrate

# Create superuser
.venv\Scripts\python.exe manage.py createsuperuser

# Django shell
.venv\Scripts\python.exe manage.py shell

# Collect static files
.venv\Scripts\python.exe manage.py collectstatic
```

## 🐛 Common Issues & Solutions

### Port Already in Use
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process
taskkill /PID <PID> /F
```

### Virtual Environment Issues
```bash
# Check if venv exists
dir .venv

# Recreate if broken
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 📱 Project Structure
```
c:\my\bca\Foodis\
├── .venv/              # Virtual environment
├── core/               # Authentication & OTP
├── client/             # Customer functionality
├── restaurant/         # Restaurant management
├── rider/              # Delivery riders
├── frontend/           # React app
├── manage.py           # Django management
├── run_server.ps1      # PowerShell startup script
├── run_server.bat      # Batch startup script
└── find_otp.py        # OTP helper script
```

## 🎯 Tips
1. **Use two terminals** - one for backend, one for frontend
2. **Keep backend running** while developing frontend
3. **Check external terminal** if IDE terminal has issues
4. **Use helper scripts** for common tasks
5. **Virtual environment** prevents dependency conflicts

## 📞 Support
- Backend runs on port 8000
- Frontend runs on port 3000
- OTPs stored in Django cache (5-minute expiry)
- All debug prints are disabled for clean output
