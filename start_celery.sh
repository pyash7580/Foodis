#!/bin/bash

echo "Starting Celery Worker..."
echo ""

if [ -d "venv" ]; then
    source venv/bin/activate
fi

celery -A foodis worker -l info

