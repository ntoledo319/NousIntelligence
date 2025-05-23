#!/bin/bash
# NOUS Personal Assistant - Public Access Workflow Script

# Display startup message
echo "🚀 Starting NOUS Personal Assistant (Public Access)..."

# Create required directories
mkdir -p static templates logs flask_session instance uploads/voice

# Set environment variables for public access
export PORT=8080
export FLASK_APP=main.py
export FLASK_ENV=development
export PYTHONUNBUFFERED=1
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export PUBLIC_ACCESS=true

# Clean up any existing processes
echo "🧹 Cleaning up any existing processes..."
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "python.*main.py" 2>/dev/null || true
pkill -f "gunicorn" 2>/dev/null || true
fuser -k 8080/tcp 2>/dev/null || true

# Start Flask application
echo "🌐 Starting Flask application on port 8080 (public mode)..."
python app.py