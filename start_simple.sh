#!/bin/bash

echo "Starting NOUS Personal Assistant (Simplified Version)..."

# Create required directories
mkdir -p flask_session uploads logs instance

# Set permissions
chmod -R 777 flask_session uploads logs instance

# Environment variables
export PORT=8080
export FLASK_ENV=production
export SECRET_KEY=$(cat .secret_key 2>/dev/null || echo "tempsecretkey")
export SESSION_SECRET=$SECRET_KEY

# Start the application using Python directly
exec python run.py