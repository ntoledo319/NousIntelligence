#!/bin/bash

# Print startup message
echo "Starting NOUS Personal Assistant..."

# Set environment variables
export PORT=8080
export FLASK_APP=main.py
export FLASK_ENV=production

# Start the application using the main entry point
python main.py