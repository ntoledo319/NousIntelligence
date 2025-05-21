#!/bin/bash

# Print startup message
echo "Starting NOUS Personal Assistant (Replit Deployment)..."

# Create required directories
mkdir -p flask_session uploads logs instance

# Set permissions
chmod -R 777 flask_session uploads logs instance

# Environment variables
export FLASK_APP=replit_app.py
export PORT=8080
export FLASK_ENV=production

# Start the application
exec python replit_app.py