#!/bin/bash

echo "Starting Foodis Development Server..."
echo ""

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed"
    exit 1
fi

echo "Running migrations..."
python3 manage.py makemigrations
python3 manage.py migrate

echo ""
echo "Starting Django server..."
python3 manage.py runserver

