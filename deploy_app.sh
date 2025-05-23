#!/bin/bash

echo "====== NOUS Deployment Script ======"
echo "Starting deployment at $(date)"

# Set environment variables for deployment
export PORT=${PORT:-8080}
export FLASK_APP=app_simple.py
export FLASK_ENV=production
export PYTHONUNBUFFERED=1

# Create necessary directories
mkdir -p static templates logs flask_session instance uploads

# Install dependencies (quiet mode for cleaner logs)
echo "Installing dependencies..."
pip install --quiet -r requirements.txt

# Start the app with gunicorn for reliability
echo "Starting app on port $PORT..."
exec gunicorn \
  --bind 0.0.0.0:$PORT \
  --workers=1 \
  --threads=4 \
  --timeout=120 \
  app_simple:app