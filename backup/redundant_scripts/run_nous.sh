#!/bin/bash

# Print startup message
echo "Starting NOUS Personal Assistant..."

# Set environment variables
export PORT=8080
export FLASK_APP=run_nous_replit.py
export FLASK_ENV=production

# Start the application
python run_nous_replit.py