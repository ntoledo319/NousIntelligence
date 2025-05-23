#!/bin/bash

# NOUS Personal Assistant - Start Script
echo "Starting NOUS Personal Assistant..."

# Ensure needed directories exist
mkdir -p static/css static/js templates flask_session logs

# Set environment variables
export FLASK_APP=main.py
export FLASK_ENV=production
export PORT=${PORT:-8080}

# Start the application using Gunicorn
exec gunicorn --bind 0.0.0.0:$PORT main:app