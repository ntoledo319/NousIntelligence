#!/bin/bash

echo "Starting NOUS Personal Assistant (Simplified Deployment)..."

# Create required directories
mkdir -p flask_session uploads logs instance

# Set permissions
chmod -R 777 flask_session uploads logs instance

# Environment variables
export FLASK_APP=simple_app.py
export PORT=8080

# Start the application using Python directly for reliable deployment
exec python simple_app.py