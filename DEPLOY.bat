@echo off
REM FOODIS DEPLOYMENT HELPER SCRIPT
REM This script helps deploy the Foodis project to production

echo.
echo ========================================
echo FOODIS DEPLOYMENT HELPER
echo ========================================
echo.

REM Check if git is available
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed or not in PATH
    echo Please install Git from https://git-scm.com
    exit /b 1
)

REM Check if npm is available
npm --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js/npm is not installed
    echo Please install from https://nodejs.org
    exit /b 1
)

echo [✓] Git found
echo [✓] Node.js found
echo.

REM Show current status
echo CURRENT GIT STATUS:
git status --short
echo.

REM Prompt for backend provider choice
echo.
echo ========================================
echo STEP 1: CHOOSE BACKEND PROVIDER
echo ========================================
echo.
echo Options:
echo   1) Railway (https://railway.app) - Recommended
echo   2) Render (https://render.com) - More stable free tier
echo   3) Heroku (https://heroku.com) - Traditional platform
echo   4) Skip backend deployment (use existing)
echo.

set /p BACKEND_CHOICE="Enter your choice (1-4): "

if "%BACKEND_CHOICE%"=="1" (
    echo.
    echo RAILWAY DEPLOYMENT INSTRUCTIONS:
    echo =====================================
    echo 1. Install Railway CLI:
    echo    npm install -g @railway/cli
    echo.
    echo 2. Login to Railway:
    echo    railway login
    echo.
    echo 3. Deploy backend:
    echo    cd d:\Foodis
    echo    railway up --detach
    echo.
    echo 4. Get your backend URL:
    echo    Visit https://railway.app/dashboard
    echo    Your URL should be: https://your-app-name.railway.app
    echo.
    echo After getting the URL, come back and run this script again
    echo to update the frontend configuration.
    echo.
) else if "%BACKEND_CHOICE%"=="2" (
    echo.
    echo RENDER DEPLOYMENT INSTRUCTIONS:
    echo =====================================
    echo 1. Go to https://render.com
    echo 2. Sign in or create account
    echo 3. Connect your GitHub repository
    echo 4. Create new Web Service with these settings:
    echo.
    echo    Build Command:
    echo    pip install -r requirements.txt && python manage.py migrate
    echo.
    echo    Start Command:
    echo    gunicorn foodis.wsgi:application --workers 2 --bind 0.0.0.0:$PORT
    echo.
    echo    Environment Variables:
    echo    - SECRET_KEY=strong_random_key_foodis_2026
    echo    - DEBUG=False
    echo    - ALLOWED_HOSTS=your-domain.onrender.com,foodis-gamma.vercel.app,.vercel.app
    echo    - DATABASE_URL=(your PostgreSQL connection string)
    echo    - GOOGLE_MAPS_API_KEY=AIzaSyDTx383dhLLt6etYN5FkxucdkuIyWQbgpA
    echo.
    echo 5. After deployment, get your URL from Render dashboard
    echo.
) else if "%BACKEND_CHOICE%"=="3" (
    echo.
    echo HEROKU DEPLOYMENT INSTRUCTIONS:
    echo =====================================
    echo 1. Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli
    echo 2. Login: heroku login
    echo 3. Create app: heroku create your-app-name
    echo 4. Push code: git push heroku main (or master)
    echo 5. Set environment variables:
    echo    heroku config:set DEBUG=False SECRET_KEY=your_key
    echo 6. Your URL: https://your-app-name.herokuapp.com
    echo.
) else (
    echo Skipping backend deployment
)

echo.
echo ========================================
echo STEP 2: UPDATE FRONTEND CONFIGURATION
echo ========================================
echo.

set /p BACKEND_URL="Enter your backend URL (e.g., https://your-domain.railway.app): "

if "%BACKEND_URL%"=="" (
    echo ERROR: Backend URL is required
    exit /b 1
)

echo.
echo Updating frontend configuration with: %BACKEND_URL%
echo.

REM Update .env.production
echo Updating frontend\.env.production
(
    echo CI=false
    echo REACT_APP_API_URL=%BACKEND_URL%
    echo REACT_APP_WS_URL=wss://%BACKEND_URL:https://=%/ws
    echo GENERATE_SOURCEMAP=false
) > frontend\.env.production

echo [✓] Updated frontend\.env.production
echo.

REM Update vercel.json (requires PowerShell for JSON handling)
echo Updating frontend/vercel.json
powershell -Command ^
    "$json = @{ version = 2; buildCommand = 'npm run build'; outputDirectory = 'build'; rewrites = @(@{ source = '/:(.*)'; destination = '/index.html' }); env = @{ DISABLE_ESLINT_PLUGIN = 'true'; SKIP_PREFLIGHT_CHECK = 'true'; GENERATE_SOURCEMAP = 'false'; CI = 'false' } } | ConvertTo-Json -Depth 10; Set-Content -Path 'frontend/vercel.json' -Value $json"

echo [✓] Updated frontend/vercel.json
echo.

echo ========================================
echo STEP 3: BUILD & TEST LOCALLY
echo ========================================
echo.

set /p RUN_LOCAL="Build and test locally? (y/n) [y]: "
if "%RUN_LOCAL%"=="" set RUN_LOCAL=y

if /i "%RUN_LOCAL%"=="y" (
    echo.
    echo Building frontend...
    cd frontend
    call npm run build
    if errorlevel 1 (
        echo ERROR: Build failed
        exit /b 1
    )
    echo [✓] Build successful
    cd ..
) else (
    echo Skipping local build
)

echo.
echo ========================================
echo STEP 4: COMMIT & PUSH CHANGES
echo ========================================
echo.

set /p COMMIT="Commit and push changes? (y/n) [y]: "
if "%COMMIT%"=="" set COMMIT=y

if /i "%COMMIT%"=="y" (
    echo.
    echo Current changes:
    git status --short
    echo.
    
    set /p MSG="Enter commit message [fix: Update backend API URL for production]: "
    if "%MSG%"=="" set MSG=fix: Update backend API URL for production
    
    git add frontend/.env.production frontend/vercel.json frontend/src/api/axiosInstance.js frontend/src/config.js
    git commit -m "%MSG%"
    if errorlevel 1 (
        echo ERROR: Commit failed
        exit /b 1
    )
    echo [✓] Changes committed
    
    echo.
    echo Pushing to remote...
    git push origin main
    if errorlevel 1 (
        echo ERROR: Push failed - Check your git configuration
        exit /b 1
    )
    echo [✓] Changes pushed to remote
) else (
    echo Remember to manually commit and push changes:
    echo   git add frontend/.env.production frontend/vercel.json
    echo   git commit -m "fix: Update backend API URL"
    echo   git push origin main
)

echo.
echo ========================================
echo DEPLOYMENT COMPLETE
echo ========================================
echo.
echo Next steps:
echo 1. Wait for Vercel to rebuild (3-5 minutes)
echo 2. Visit: https://foodis-gamma.vercel.app/client
echo 3. Check browser console for errors (F12 → Console)
echo 4. Test functionality (Browse → Add to Cart → Checkout)
echo.
echo Monitor deployment:
echo   - Vercel: https://vercel.com/dashboard
echo   - Logs: https://vercel.com/dashboard/your-project/settings/functions
echo.

pause
