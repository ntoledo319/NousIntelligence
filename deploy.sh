#!/bin/bash

echo "=== NOUS Personal Assistant Deployment Script ==="
echo "Starting deployment process at $(date)"

# Set up environment variables
export PORT=${PORT:-8080}
export FLASK_APP=nous_deployment.py
export FLASK_ENV=production
export PYTHONUNBUFFERED=1

# Make sure all dependencies are installed
pip install flask gunicorn psutil requests werkzeug

# Start the application with Gunicorn
echo "Starting NOUS on port $PORT..."
exec gunicorn \
  --bind 0.0.0.0:$PORT \
  --workers=1 \
  --timeout=30 \
  nous_deployment:app