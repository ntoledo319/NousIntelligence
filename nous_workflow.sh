#!/bin/bash
# NOUS Personal Assistant - Workflow Script

echo "🚀 Starting NOUS Personal Assistant workflow..."

# Create required directories
mkdir -p logs flask_session instance

# Set environment variables
export FLASK_ENV=production
export PORT=8080
export PYTHONUNBUFFERED=1

# Kill any existing processes
pkill -f "python.*main.py" 2>/dev/null || true
pkill -f "gunicorn" 2>/dev/null || true
fuser -k 8080/tcp 2>/dev/null || true

# Start with gunicorn
echo "✅ Starting Gunicorn server"
exec /home/runner/workspace/.pythonlibs/bin/gunicorn --bind 0.0.0.0:8080 --workers 2 --timeout 120 wsgi:app