@echo off
echo Opening external terminal for Foodis project...
echo.
echo Starting new Command Prompt window...
start "Foodis Backend" cmd /k "cd /d c:\my\bca\Foodis && echo Foodis Project - Backend Server && echo Type: run_server.bat && echo Or: .venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000 && cmd"
echo.
echo Starting new terminal for Frontend...
start "Foodis Frontend" cmd /k "cd /d c:\my\bca\Foodis\frontend && echo Foodis Project - Frontend && echo Type: npm start && cmd"
echo.
echo External terminals opened!
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
pause
