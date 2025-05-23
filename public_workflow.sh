#!/bin/bash
# NOUS Personal Assistant - Public Access Workflow

echo "🚀 Starting NOUS Personal Assistant (Public Access Mode)..."

# Create required directories
mkdir -p static templates logs flask_session instance uploads/voice

# Set environment variables
export PORT=8080
export FLASK_APP=main.py
export FLASK_ENV=development
export PYTHONUNBUFFERED=1
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export PUBLIC_ACCESS=true

# Kill any existing processes that might conflict
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "python.*main.py" 2>/dev/null || true
pkill -f "gunicorn" 2>/dev/null || true

echo "🌐 Starting Flask application on port 8080 (Public Mode)..."
exec python app.py