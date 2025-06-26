#!/bin/bash

# NOUS Personal Assistant - Quick Run Script
# This script ensures your app runs without any login requirements or blank pages

echo "======= NOUS Quick Run ======="
echo "Starting at $(date)"

# Create required directories
mkdir -p static templates logs

# Clean up any existing processes
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "gunicorn.*app:app" 2>/dev/null || true
pkill -f "python.*simple_app.py" 2>/dev/null || true

# Set environment variables
export PORT=8080
export FLASK_APP=simple_app.py
export PYTHONUNBUFFERED=1

# Start the application
echo "Starting simple app on port 8080..."
python simple_app.py