#!/bin/bash

# NOUS Personal Assistant - Simple Public Runner
# This script runs the app in public mode

echo "======= Starting NOUS Public App ======="
echo "Starting at $(date)"

# Create required directories
mkdir -p static templates logs instance flask_session uploads

# Set environment variables
export PORT=8080
export FLASK_APP=app.py
export FLASK_ENV=production
export PYTHONUNBUFFERED=1

# Set public access flags
export PUBLIC_ACCESS=true
export REPLIT_PUBLIC=true

# Start the application
echo "Starting public application on port 8080..."
exec python app.py