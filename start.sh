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

# Set environment variables
export SECRET_KEY=$(cat .secret_key)
export PORT=8080
export FLASK_ENV=${FLASK_ENV:-"production"}
export PYTHONUNBUFFERED=1

# Set the Python path to include the current directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Set up deployment logs
mkdir -p logs
TIMESTAMP=$(date +%Y%m%d)
echo "[$(date +'%Y-%m-%d %H:%M:%S')] INFO in deployment_logger: [STARTUP] Application starting up" >> "logs/deployment_${TIMESTAMP}.log"

# Kill any existing processes that might conflict
pkill -f "python.*main.py" 2>/dev/null || true
pkill -f "gunicorn" 2>/dev/null || true
fuser -k 8080/tcp 2>/dev/null || true

echo "🌐 Starting web server on port 8080..."

# Check if gunicorn is available
if command -v gunicorn &> /dev/null; then
    # Use full path to gunicorn to ensure we're using the right executable
    GUNICORN_PATH=$(which gunicorn)
    echo "✅ Using gunicorn at: $GUNICORN_PATH"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] INFO in deployment_logger: [STARTUP] Starting gunicorn from: $GUNICORN_PATH" >> "logs/deployment_${TIMESTAMP}.log"
    
    # Start with explicit gunicorn command using wsgi.py
    exec $GUNICORN_PATH \
        --bind 0.0.0.0:8080 \
        --workers 2 \
        --timeout 120 \
        --access-logfile - \
        --error-logfile - \
        --log-level info \
        "wsgi:app"
else
    echo "⚠️ Gunicorn not found, using Flask development server (not recommended for production)"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] WARNING in deployment_logger: [STARTUP] Using development server in production" >> "logs/deployment_${TIMESTAMP}.log"
    python main.py
fi