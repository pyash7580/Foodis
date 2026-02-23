# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 8000

# Set work directory
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Run script as entrypoint (ensures CMD can run it)
RUN chmod +x run.sh

# Expose port
EXPOSE 8000

# Start command
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn foodis.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT"]
