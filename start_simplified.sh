#!/bin/bash

# Print startup message
echo "Starting NOUS Personal Assistant (Simplified Version)..."

# Create required directories
mkdir -p flask_session uploads logs instance

# Set permissions
chmod -R 777 flask_session uploads logs instance

# Environment variables
export FLASK_APP=app_simplified.py
export PORT=8080
export FLASK_ENV=production
export AUTO_CREATE_TABLES=true

# Start the application using Python directly for reliable deployment
exec python app_simplified.py