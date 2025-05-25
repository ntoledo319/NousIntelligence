#!/bin/bash

# NOUS Personal Assistant - Complete App Runner
# This script ensures your app runs publicly and fixes blank page issues

echo "======= NOUS Complete App ======="
echo "Starting at $(date)"

# Create required directories
mkdir -p static templates logs instance flask_session uploads

# Set environment variables
export PORT=8080
export FLASK_APP=complete_app.py
export FLASK_ENV=production
export PYTHONUNBUFFERED=1
export PUBLIC_ACCESS=true

# Clean up any existing processes
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "gunicorn.*app:app" 2>/dev/null || true
pkill -f "python.*complete_app.py" 2>/dev/null || true

echo "Starting the complete application on port 8080..."
python complete_app.py