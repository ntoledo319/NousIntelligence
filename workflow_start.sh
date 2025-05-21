#!/bin/bash

echo "Starting NOUS Personal Assistant..."

# Create necessary directories
mkdir -p flask_session uploads logs

# Set proper permissions
chmod -R 777 flask_session
chmod -R 777 uploads

# Set environment variables
export FLASK_APP=main.py
export FLASK_ENV=production
export PORT=8080

# Start Flask application
exec gunicorn --bind 0.0.0.0:8080 --timeout 120 --workers 2 main:app
