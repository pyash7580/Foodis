@echo off
SETLOCAL ENABLEDELAYEDEXPANSION
title Foodis Safe Start Control Center

echo ============================================================
echo           FOODIS PROJECT - SAFE START SYSTEM
echo ============================================================
echo.

set "SCRIPT_DIR=%~dp0"

:: 1. Cleanup old processes
echo [1/5] Cleaning up existing processes...
taskkill /FI "WINDOWTITLE eq Foodis Backend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Foodis Frontend*" /F >nul 2>&1
:: Kill any node/python processes running on our ports
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do taskkill /F /PID %%a >nul 2>&1
echo Done.

:: 2. Environment Setup
echo [2/5] Setting up environment...
set "PYTHON_EXE="
if exist "%SCRIPT_DIR%\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%SCRIPT_DIR%\.venv\Scripts\python.exe"
) else if exist "%SCRIPT_DIR%venv\Scripts\python.exe" (
    set "PYTHON_EXE=%SCRIPT_DIR%venv\Scripts\python.exe"
) else (
    echo ERROR: Python virtual environment not found! 
    echo Please create one at .venv or venv.
    pause
    exit /b 1
)

:: Ensure cache table exists
"%PYTHON_EXE%" manage.py createcachetable >nul 2>&1
"%PYTHON_EXE%" manage.py migrate >nul 2>&1
echo Done.

:: 3. Start Backend
echo [3/5] Starting Django Backend (Port 8000)...
start "Foodis Backend" cmd /k "title Foodis Backend && cd /d "%SCRIPT_DIR%" && "%PYTHON_EXE%" manage.py runserver 127.0.0.1:8001"

:: 4. Wait for Backend to be READY
echo [4/5] Waiting for Backend to respond...
set "RETRIES=0"
:wait_loop
set /a RETRIES+=1
if %RETRIES% GTR 30 (
    echo.
    echo ERROR: Backend failed to start within 30 seconds.
    echo Please check the "Foodis Backend" window for errors.
    pause
    exit /b 1
)
powershell -Command "(Invoke-WebRequest -Uri http://127.0.0.1:8001 -UseBasicParsing).StatusCode" >nul 2>&1
if !errorlevel! NEQ 0 (
    <nul set /p =.
    timeout /t 1 /nobreak >nul
    goto wait_loop
)
echo.
echo Backend is ONLINE.

:: 5. Start Frontend
echo [5/5] Starting React Frontend (Port 3000)...
if exist "%SCRIPT_DIR%frontend" (
    start "Foodis Frontend" cmd /k "title Foodis Frontend && cd /d "%SCRIPT_DIR%frontend" && npm start"
) else (
    echo ERROR: Frontend directory not found!
)

echo.
echo ============================================================
echo   SUCCESS: All systems initiated!
echo   - Backend: http://localhost:8000
echo   - Frontend: http://localhost:3000
echo.  
echo   KEEP THE POPUP WINDOWS OPEN WHILE WORKING.
echo   Use STOP_SERVERS.bat to close everything.
echo ============================================================
echo.
pause
