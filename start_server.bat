@echo off
echo Starting Foodis Development Server...
echo.

echo Checking Python...
if exist .venv\Scripts\python.exe (
    echo Found Python in virtual environment
    set PYTHON_CMD=.venv\Scripts\python.exe
) else (
    echo Using system Python
    set PYTHON_CMD=python
)
%PYTHON_CMD% --version
if errorlevel 1 (
    echo Python is not installed or not available
    pause
    exit /b 1
)

echo.
echo Activating virtual environment...
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    echo Virtual environment activated
) else (
    echo No virtual environment found, using system Python
)

echo.
echo Running migrations...
%PYTHON_CMD% manage.py makemigrations
%PYTHON_CMD% manage.py migrate

echo.
echo Starting Django server...
%PYTHON_CMD% manage.py runserver 0.0.0.0:8000

pause
