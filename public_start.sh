#!/bin/bash
# NOUS Personal Assistant - Public Access Startup Script
# This script starts a version of the application that's publicly accessible without login requirements

echo "Starting NOUS Personal Assistant (Public Access Version)..."

# Create necessary directories
mkdir -p logs

# Set environment variables for public access
export PORT=8080
export FLASK_ENV=production
export FLASK_APP=public_app.py
export REPLIT_PUBLIC_ACCESS=true

# Generate a secret key if none exists
if [ ! -f ".secret_key" ]; then
    echo "Generating new secret key..."
    python -c "import secrets; print(secrets.token_hex(24))" > .secret_key
    chmod 600 .secret_key
fi

# Load secret key
export SECRET_KEY=$(cat .secret_key)

# Disable authentication for public access
export SKIP_AUTH=true

echo "Starting public web server on port 8080..."
python public_app.py