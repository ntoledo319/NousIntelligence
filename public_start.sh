#!/bin/bash

# NOUS Personal Assistant - Public Deployment Starter
# This script starts the application for production deployment

echo "===== NOUS Personal Assistant - Public Deployment ====="
echo "Starting application in production mode..."

# Create necessary directories
mkdir -p static/css static/js templates flask_session logs

# Set environment variables
export FLASK_APP=main.py
export FLASK_ENV=production

# Get the port from environment or use 8080 as default
PORT="${PORT:-8080}"
echo "Using port: $PORT"

# Run the application with gunicorn if available
if command -v gunicorn &>/dev/null; then
    echo "Starting with Gunicorn..."
    gunicorn --bind 0.0.0.0:$PORT main:app --log-level info
else
    echo "Gunicorn not found, using Flask development server..."
    python main.py
fi