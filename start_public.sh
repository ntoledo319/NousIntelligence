#!/bin/bash

# NOUS Personal Assistant - Public Starter Script
# Use this script to start your app without Replit login requirements

echo "======= Starting NOUS Public App ======="
echo "Starting at $(date)"

# Create required directories
mkdir -p static templates logs instance flask_session uploads

# Set environment variables
export PORT=8080
export FLASK_APP=app.py
export FLASK_ENV=production
export PYTHONUNBUFFERED=1
export PUBLIC_ACCESS=true

# Start the application
echo "Starting public application on port 8080..."
python app.py