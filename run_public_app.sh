#!/bin/bash

# NOUS Personal Assistant - Public App Runner
# This script ensures your app runs without any login requirements

echo "======= NOUS Public App Runner ======="
echo "Starting at $(date)"

# Create required directories
mkdir -p static templates logs

# Clean up any existing processes
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "gunicorn.*app:app" 2>/dev/null || true

# Set environment variables
export PORT=8080
export FLASK_APP=public_app.py
export PYTHONUNBUFFERED=1
export PUBLIC_ACCESS=true

# Start the application
echo "Starting public app on port 8080..."
python public_app.py