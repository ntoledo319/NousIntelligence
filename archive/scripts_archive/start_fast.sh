#!/bin/bash
# Ultra-Fast Production Startup

set -e

echo "🚀 NOUS Production - Fast Startup"

# Create directories in parallel
mkdir -p logs static templates flask_session instance &

# Set environment for maximum speed
export FLASK_ENV=production
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1
export WERKZEUG_RUN_MAIN=true

# Get configuration
PORT=${PORT:-8080}
HOST=${HOST:-0.0.0.0}

echo "📊 Starting on $HOST:$PORT"

# Use optimized app if available, fallback to main
if [ -f "app_optimized.py" ]; then
    echo "🔧 Using optimized application"
    exec gunicorn --config gunicorn.conf.py app_optimized:app
elif [ -f "gunicorn.conf.py" ]; then
    echo "🔧 Using Gunicorn production server"
    exec gunicorn --config gunicorn.conf.py app:app
else
    echo "🔧 Using direct Python startup"
    exec python main.py
fi
