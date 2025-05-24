#!/bin/bash

# NOUS Personal Assistant - Single Public App Runner
# This script runs the consolidated app with no login required

echo "======= Starting NOUS Public Application ======="
echo "Starting at $(date)"

# Create required directories
mkdir -p static templates logs instance flask_session uploads

# Set environment variables for public access
export PORT=8080
export FLASK_APP=one_app.py
export FLASK_ENV=production
export PUBLIC_MODE=true
export PYTHONUNBUFFERED=1

# Clean up any existing processes
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "gunicorn.*app:app" 2>/dev/null || true

echo "Starting public application on port $PORT..."
exec python one_app.py