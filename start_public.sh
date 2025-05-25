#!/bin/bash

# NOUS Personal Assistant - Public Start Script
# This script ensures the application is publicly accessible without login

echo "======= NOUS Public Start ======="
echo "Starting at $(date)"

# Create required directories
mkdir -p static templates logs

# Clean up any existing processes
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "python.*simple_app.py" 2>/dev/null || true

# Set environment variables for public access
export PORT=8080
export FLASK_APP=simple_app.py
export PYTHONUNBUFFERED=1
export PUBLIC_ACCESS=true

echo "Starting public app on port 8080..."
python simple_app.py