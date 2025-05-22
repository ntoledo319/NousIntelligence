#!/bin/bash

# Print startup message
echo "Starting NOUS Personal Assistant..."

# Set environment variables
export FLASK_APP=simple_app.py
export PORT=8080
export FLASK_ENV=production

# Start the application
python simple_app.py