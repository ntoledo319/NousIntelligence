#!/bin/bash

# NOUS Personal Assistant - Startup Script
# This script ensures the app starts properly and fixes routing issues

echo "=== NOUS Personal Assistant ==="
echo "Starting application..."

# Kill any existing processes that might be using our ports
pkill -f "python main.py" 2>/dev/null || true
pkill -f "python app.py" 2>/dev/null || true
pkill -f "python app_direct.py" 2>/dev/null || true

# Clear port 8080 (used by Replit)
fuser -k 8080/tcp 2>/dev/null || true

# Start the application with our direct version
python app_direct.py