#!/bin/bash
# NOUS Personal Assistant - Workflow Startup Script

echo "🚀 Starting NOUS Personal Assistant..."

# Create required directories
mkdir -p static templates logs flask_session instance uploads/voice

# Set environment variables
export PORT=8080
export FLASK_APP=main.py
export FLASK_ENV=development
export PYTHONUNBUFFERED=1
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Kill any existing processes that might conflict
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "python.*main.py" 2>/dev/null || true
pkill -f "gunicorn" 2>/dev/null || true

echo "🌐 Starting Flask development server on port 8080..."
python app.py