#!/bin/bash

# Simple script to run the NOUS application consistently

echo "=== Starting NOUS Personal Assistant ==="
echo "$(date): Initializing application"

# Kill any existing processes
pkill -f "python.*app.py" || true
pkill -f "gunicorn.*app:app" || true

# Set up environment variables
export PORT=5000
export FLASK_APP=app.py
export FLASK_ENV=development
export PYTHONUNBUFFERED=1

# Make sure directories exist
mkdir -p logs flask_session static templates instance uploads

# Run the application
echo "Starting app on port $PORT..."
python app.py