#!/bin/bash

echo "=== Starting NOUS Personal Assistant ==="
echo "Starting at $(date)"

# Set up environment variables
export PORT=${PORT:-8080}
export FLASK_APP=nous_app.py
export FLASK_ENV=${FLASK_ENV:-production}
export PYTHONUNBUFFERED=1

# Make sure all dependencies are installed
pip install flask gunicorn psutil requests werkzeug flask-sqlalchemy

# Start the application
echo "Starting NOUS on port $PORT..."
python nous_app.py