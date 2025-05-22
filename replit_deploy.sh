#!/bin/bash
# Replit deployment script for NOUS Personal Assistant

echo "🚀 Starting NOUS Personal Assistant for Replit..."

# Create required directories
mkdir -p static templates logs

# Generate a secret key if it doesn't exist
if [ ! -f ".secret_key" ]; then
    echo "🔑 Generating new secret key..."
    python -c "import secrets; print(secrets.token_hex(24))" > .secret_key
    chmod 600 .secret_key
fi

# Set secret key and environment variables
export SECRET_KEY=$(cat .secret_key)
export PORT=8080
export FLASK_ENV=production
export PYTHONUNBUFFERED=1
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start the application using the Replit-specific app file
echo "🌐 Starting web server on port 8080..."
exec python replit_app.py