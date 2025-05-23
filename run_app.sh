#!/bin/bash

# Run App Script for NOUS Personal Assistant
# This script sets up the environment and starts the application

echo "===== Starting NOUS Personal Assistant ====="

# Create required directories
mkdir -p static/css static/js templates/smart_shopping logs flask_session

# Set environment variables
export PORT=5000
export FLASK_APP=app.py

# Run the application
echo "Starting application on port 5000..."
python main.py