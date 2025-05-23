#!/bin/bash
# NOUS Personal Assistant - Public Access Mode

# Clear terminal
clear

echo "🚀 Starting NOUS Personal Assistant in Public Mode..."

# Create required directories
mkdir -p static templates logs flask_session instance uploads/voice

# Set environment variables
export PORT=8080
export FLASK_APP=main.py
export FLASK_ENV=development
export PYTHONUNBUFFERED=1
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export PUBLIC_ACCESS=true

# Ensure we have a clean start
echo "🧹 Cleaning up any existing processes..."
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "python.*main.py" 2>/dev/null || true
pkill -f "gunicorn" 2>/dev/null || true
fuser -k 8080/tcp 2>/dev/null || true

echo "🌐 Starting Flask application on port 8080..."
cd "$(dirname "$0")"
python app.py