#!/bin/bash

# NOUS Personal Assistant - Starter Script
# This script ensures the app starts properly on Replit

echo "=== NOUS Personal Assistant ==="
echo "Starting application..."

# Kill any running Python processes that might be using our ports
pkill -f "python main.py" || true
pkill -f "python app.py" || true
pkill -f "python run.py" || true

# Make sure we use port 5000
export PORT=5000

# Start the application
python run.py