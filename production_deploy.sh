#!/bin/bash

# Print startup message
echo "Starting NOUS Personal Assistant (Production Version)..."

# Create required directories
mkdir -p flask_session uploads logs instance

# Set permissions
chmod -R 777 flask_session uploads logs instance

# Environment variables
export FLASK_APP=production_app.py
export PORT=8080
export FLASK_ENV=production
export AUTO_CREATE_TABLES=true

# Check if gunicorn is available, use it if possible
if command -v gunicorn &> /dev/null; then
    echo "Starting with Gunicorn for production performance..."
    exec gunicorn --bind 0.0.0.0:8080 --workers 2 --threads 2 --timeout 120 'production_app:app'
else
    # Fall back to the Flask development server if Gunicorn isn't available
    echo "Gunicorn not found, starting with Flask development server..."
    exec python production_app.py
fi