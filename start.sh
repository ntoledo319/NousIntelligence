#!/bin/bash

# NOUS Personal Assistant - Start Script
echo "Starting NOUS Personal Assistant..."

# Ensure needed directories exist
mkdir -p static/css static/js templates flask_session logs

# Set environment variables
export FLASK_APP=main.py
export FLASK_ENV=production
export PORT=${PORT:-5000}

# Run the Flask application directly
python main.py