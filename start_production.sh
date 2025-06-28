#!/bin/bash
# Optimized Production Startup Script

set -e  # Exit on any error

echo "🚀 Starting NOUS Production Build..."

# Create required directories
mkdir -p logs static templates flask_session instance

# Set production environment variables for optimal performance
export FLASK_ENV=production
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1
export WERKZEUG_RUN_MAIN=true
export PIP_NO_CACHE_DIR=1
export PIP_DISABLE_PIP_VERSION_CHECK=1

# Get port from environment
PORT=${PORT:-8080}
HOST=${HOST:-0.0.0.0}

echo "📊 Starting application on $HOST:$PORT"

# Start with Gunicorn for production performance
if [ -f "gunicorn.conf.py" ]; then
    echo "🔧 Using Gunicorn production server..."
    exec gunicorn --config gunicorn.conf.py app:app
else
    echo "🔧 Using Flask development server..."
    exec python main.py
fi