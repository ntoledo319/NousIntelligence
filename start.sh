#!/bin/bash
# Start script for NOUS application
# This script ensures the application runs continuously in production

# Environment setup
export FLASK_APP=main.py
export PYTHONUNBUFFERED=1

# Function to handle graceful shutdown
function cleanup() {
    echo "Received shutdown signal, gracefully stopping services..."
    kill -TERM $PID
    wait $PID
    echo "Application stopped."
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo "Starting NOUS application with Gunicorn..."

# Start Gunicorn with optimized settings
exec gunicorn --config gunicorn_config.py --bind 0.0.0.0:5000 --reuse-port --worker-tmp-dir /dev/shm --preload --workers=2 --threads=4 main:app &

PID=$!

# Keep the script running to maintain the container alive
wait $PID