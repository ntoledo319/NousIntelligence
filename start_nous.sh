#!/bin/bash

# NOUS Personal Assistant Starter
# This script ensures your app runs on the correct port

echo "===== NOUS Personal Assistant ====="
echo "Starting your app..."

# Kill any existing processes that might be using our ports
pkill -f "python main.py" 2>/dev/null || true
pkill -f "python app.py" 2>/dev/null || true
pkill -f "python app_direct.py" 2>/dev/null || true
pkill -f "python nous_app.py" 2>/dev/null || true

# Set port to 5000 to avoid conflicts with Replit
export PORT=5000

# Run the simplified app that should display properly
python nous_app.py