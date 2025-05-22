#!/bin/bash
# NOUS Personal Assistant - Launch Script
# This script is designed to be used with Replit workflows

echo "🚀 Launching NOUS Personal Assistant..."

# Create required directories
mkdir -p static templates logs flask_session instance

# Generate a secret key if it doesn't exist
if [ ! -f ".secret_key" ]; then
    echo "🔑 Generating new secret key..."
    python -c "import secrets; print(secrets.token_hex(24))" > .secret_key
    chmod 600 .secret_key
fi

# Set environment variables
export SECRET_KEY=$(cat .secret_key)
export PORT=8080
export FLASK_ENV=production
export PYTHONUNBUFFERED=1

# Set up deployment logs
mkdir -p logs
TIMESTAMP=$(date +%Y%m%d)
echo "[$(date +'%Y-%m-%d %H:%M:%S')] INFO in deployment_logger: [STARTUP] Application starting from launch script" >> "logs/deployment_${TIMESTAMP}.log"

echo "🌐 Starting web server on port 8080..."

# Check if gunicorn is available and use it for production
if command -v gunicorn &> /dev/null; then
    GUNICORN_PATH=$(which gunicorn)
    echo "✅ Using gunicorn for production deployment"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] INFO in deployment_logger: [STARTUP] Starting gunicorn from: $GUNICORN_PATH" >> "logs/deployment_${TIMESTAMP}.log"
    
    # Use direct gunicorn command with explicit path to avoid issues
    $GUNICORN_PATH --bind 0.0.0.0:8080 --workers 2 --timeout 120 wsgi:app
else
    # Fall back to Flask development server if necessary
    echo "⚠️ Gunicorn not found, using Flask development server"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] WARNING in deployment_logger: [STARTUP] Using development server" >> "logs/deployment_${TIMESTAMP}.log"
    python main.py
fi