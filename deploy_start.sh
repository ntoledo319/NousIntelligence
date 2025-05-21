#!/bin/bash

# Print startup message
echo "Starting NOUS Personal Assistant (Deployment Version)..."

# Create required directories
mkdir -p flask_session uploads logs instance

# Set permissions
chmod -R 777 flask_session uploads logs instance

# Environment variables
export FLASK_APP=deploy.py
export PORT=8080
export FLASK_ENV=production

# Start the application using Python directly for reliable deployment
exec python deploy.py