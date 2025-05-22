#!/bin/bash
# NOUS Personal Assistant - Unified Startup Script

echo "🚀 Starting NOUS Personal Assistant..."

# Create required directories
mkdir -p static templates logs flask_session instance

# Generate a secret key if it doesn't exist
if [ ! -f ".secret_key" ]; then
    echo "🔑 Generating new secret key..."
    python -c "import secrets; print(secrets.token_hex(24))" > .secret_key
    chmod 600 .secret_key
fi

# Set secret key and required environment variables
export SECRET_KEY=$(cat .secret_key)
export PORT=8080
export FLASK_ENV=${FLASK_ENV:-"production"}
export PYTHONUNBUFFERED=1

# Set the Python path to include the current directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo "🌐 Starting web server on port 8080..."

# Try to use gunicorn for production quality, but fall back to regular Flask if needed
if command -v gunicorn &> /dev/null; then
    echo "✅ Using gunicorn for production-ready server"
    gunicorn 'main:app' --bind '0.0.0.0:8080' --workers 2 --access-logfile - --error-logfile -
else
    echo "⚠️ Gunicorn not found, using Flask development server"
    python main.py
fi