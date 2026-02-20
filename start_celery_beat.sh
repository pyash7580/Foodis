#!/bin/bash

echo "Starting Celery Beat (Scheduler)..."
echo ""

if [ -d "venv" ]; then
    source venv/bin/activate
fi

celery -A foodis beat -l info

