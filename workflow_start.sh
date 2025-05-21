#!/bin/bash
# NOUS Application Workflow Startup Script
# This script starts the application in a Replit workflow

echo "Starting NOUS application in workflow..."

# Create required directories
mkdir -p flask_session uploads logs instance

# Set permissions
chmod -R 777 flask_session uploads logs

# Environment variables
export FLASK_APP=main.py
export FLASK_ENV=production
export PORT=8080

# Start the application using Gunicorn for stability
exec gunicorn -c gunicorn_config.py main:app