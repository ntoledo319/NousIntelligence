#!/bin/bash

# NOUS Personal Assistant - Simple Run Script
# This script starts the application for development or deployment

echo "======= Starting NOUS Application ======="
echo "Starting at $(date)"

# Ensure required directories exist
mkdir -p logs static templates flask_session instance uploads

# Set up environment variables
export PORT=8080
export FLASK_APP=app.py
export PYTHONUNBUFFERED=1

# Kill any existing processes
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "gunicorn.*app:app" 2>/dev/null || true

# Start the application
echo "Starting application on port $PORT..."
python app.py