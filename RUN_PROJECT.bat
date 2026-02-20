@echo off
SETLOCAL ENABLEDELAYEDEXPANSION
echo ========================================
echo Starting Foodis Project (Stable Mode)
echo ========================================
echo.
REM Resolve script directory
set "SCRIPT_DIR=%~dp0"

REM Detect python executable (prefer project .venv)
set "PYTHON_EXE="
if exist "%SCRIPT_DIR%\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%SCRIPT_DIR%\.venv\Scripts\python.exe"
) else if exist "%SCRIPT_DIR%venv\Scripts\python.exe" (
    set "PYTHON_EXE=%SCRIPT_DIR%venv\Scripts\python.exe"
) else (
    for %%P in (python python3) do if not defined PYTHON_EXE (
        for /f "usebackq tokens=1" %%I in (`where %%P 2^>nul`) do if exist "%%I" set "PYTHON_EXE=%%I"
    )
)

if not defined PYTHON_EXE (
    echo ERROR: No Python interpreter found. Install Python or create a virtualenv at .venv\r
    pause
    exit /b 1
)

echo Using Python: %PYTHON_EXE%

REM Check for Node and npm
echo Checking Node/NPM availability...
set "NODE_AVAILABLE=0"
for /f "usebackq tokens=1" %%I in (`where node 2^>nul`) do if exist "%%I" set "NODE_AVAILABLE=1"
set "NPM_AVAILABLE=0"
for /f "usebackq tokens=1" %%I in (`where npm 2^>nul`) do if exist "%%I" set "NPM_AVAILABLE=1"

if %NODE_AVAILABLE%==0 (
    echo Warning: Node.js not found in PATH. Frontend dev server may not run.
)
if %NPM_AVAILABLE%==0 (
    echo Warning: npm not found in PATH. Frontend dev server may not run.
)

REM 1. Start Django Backend in a new window using project python
echo Starting Django Backend...
start "Foodis Backend" cmd /k "title Foodis Backend && cd /d "%SCRIPT_DIR%" && "%PYTHON_EXE%" manage.py runserver 0.0.0.0:8000"

REM 2. Wait for backend to become available (up to 20s)
echo Waiting for backend to start (up to 20 seconds)...
set "BACKEND_OK=0"
for /L %%i in (1,1,20) do (
    powershell -Command "try { (Invoke-WebRequest -UseBasicParsing -Uri http://localhost:8000 -TimeoutSec 2).StatusCode } catch { exit 1 }" > nul 2>&1
    if !errorlevel! EQU 0 (
        set "BACKEND_OK=1"
        goto :backend_ready
    )
    timeout /t 1 /nobreak > nul
)
:backend_ready
if "%BACKEND_OK%"=="1" (
    echo Backend is responding at http://localhost:8000
) else (
    echo Warning: Backend did not respond within the timeout. Frontend may fail to connect.
)

REM 3. Start React Frontend in a new window. Prefer dev server; fallback to serving built assets.
echo Starting React Frontend...
if exist "%SCRIPT_DIR%frontend" (
    if %NPM_AVAILABLE%==1 (
        start "Foodis Frontend" cmd /k "title Foodis Frontend && cd /d "%SCRIPT_DIR%frontend" && npm start"
    ) else if exist "%SCRIPT_DIR%frontend\build" (
        echo npm not available; serving built frontend at port 3000 using npx serve (if available)...
        start "Foodis Frontend (serve build)" cmd /k "title Foodis Frontend && cd /d "%SCRIPT_DIR%frontend" && npx serve -s build -l 3000"
    ) else (
        echo ERROR: Cannot start frontend dev server - npm not found and no build directory present.
        echo To run frontend, install Node.js and npm, then run: cd frontend && npm install && npm start
    )
) else (
    echo ERROR: frontend directory not found in %SCRIPT_DIR%
)

cd ..

echo.
echo ========================================
echo Servers have been launched in separate windows!
echo ========================================
echo.
echo Backend URL: http://localhost:8000
echo Frontend URL: http://localhost:3000
echo.
echo DO NOT CLOSE THE POPUP WINDOWS.
echo To stop servers, use STOP_SERVERS.bat
echo.
pause
ENDLOCAL
