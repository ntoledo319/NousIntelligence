#!/bin/bash

# Environment variables
export FLASK_APP=main.py
export FLASK_ENV=development
export PORT=8080

# Create necessary directories
mkdir -p flask_session uploads logs

# Set proper permissions
chmod -R 777 flask_session
chmod -R 777 uploads

# Start Flask application with Gunicorn for stability
exec gunicorn --bind 0.0.0.0:8080 --workers 2 --threads 2 main:app