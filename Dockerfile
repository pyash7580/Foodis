# ==========================================
# Phase 1: Build the React Frontend
# ==========================================
FROM node:18-alpine as frontend-builder

WORKDIR /app/frontend

# Copy package files and install dependencies
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci || npm install

# Copy frontend source and build
COPY frontend/ .
RUN npm run build

# ==========================================
# Phase 2: Setup Python Backend & Serve
# ==========================================
FROM python:3.11-slim

# Prevent python from writing pyc files and keep stdout unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend project
COPY . .

# Copy the compiled React build from Phase 1 into Django's static/frontend directory
# This allows Django matching with WhiteNoise to serve the frontend directly
COPY --from=frontend-builder /app/frontend/build /app/frontend/build

# Setup environment variables for collectstatic
ENV DJANGO_SETTINGS_MODULE=foodis.settings
ENV SECRET_KEY=dummy_secret_key_for_build

# Collect static files (including the React build if configured in settings.py)
RUN python manage.py collectstatic --noinput

# Expose port 8000 for Railway/Render/AWS
EXPOSE 8000

# We use Daphne instead of Gunicorn because Foodis uses WebSockets (Channels)
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "foodis.asgi:application"]
