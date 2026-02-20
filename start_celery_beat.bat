@echo off
echo Starting Celery Beat (Scheduler)...
echo.

if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

celery -A foodis beat -l info

pause

