#!/bin/bash
# Public deployment script for NOUS Personal Assistant

echo "🚀 Deploying NOUS Personal Assistant..."

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

# Install any critical dependencies
echo "📦 Checking for required packages..."

# Start the application with gunicorn for better performance if available
echo "🌐 Starting web server on port 8080..."
if command -v gunicorn &> /dev/null; then
    echo "✅ Using gunicorn for production server"
    exec gunicorn 'nous_public:app' --bind '0.0.0.0:8080' --workers 1 --access-logfile - --error-logfile -
else
    echo "⚠️ Using Flask development server"
    exec python nous_public.py
fi