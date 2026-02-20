@echo off
echo Starting Celery Worker...
echo.

if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

celery -A foodis worker -l info

pause

