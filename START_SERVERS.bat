@echo off
echo ========================================
echo Starting Foodis Servers (Permanent Mode)
echo ========================================
echo.

REM 1. Start Django Backend in a new window
echo Starting Django Backend...
start "Foodis Backend" cmd /k "title Foodis Backend && python manage.py runserver 0.0.0.0:8000"

REM 2. Start React Frontend in a new window
echo Starting React Frontend...
cd frontend
start "Foodis Frontend" cmd /k "title Foodis Frontend && npm start"
cd ..

echo.
echo ========================================
echo Servers have been launched in separate windows!
echo ========================================
echo.
echo Backend URL: http://127.0.0.1:8000
echo Frontend URL: http://localhost:3000
echo.
echo Health Check: http://127.0.0.1:8000/api/health/
echo.
echo DO NOT CLOSE THE POPUP WINDOWS.
echo To stop servers, run STOP_SERVERS.bat or close the windows manually.
echo.
pause
