#!/bin/bash

# NOUS Personal Assistant Starter Script
# This script ensures the app runs on the correct port

echo "===== NOUS Personal Assistant ====="
echo "Starting your app..."

# Create necessary directories
mkdir -p static/css static/js templates flask_session logs

# Set port to 5000 to avoid conflicts 
export PORT=5000
export FLASK_APP=main.py
export FLASK_ENV=development

# Run the application
echo "Starting Flask application on port 5000..."
python main.py