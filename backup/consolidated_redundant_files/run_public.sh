#!/bin/bash

# NOUS Personal Assistant - Public Runner
# This script ensures your app is publicly accessible without login requirements

echo "======= NOUS Public Application ======="
echo "Starting at $(date)"

# Create required directories
mkdir -p static templates logs

# Clean up any existing processes
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "python.*one_public_app.py" 2>/dev/null || true

# Set environment variables for public access
export PORT=8080
export PYTHONUNBUFFERED=1
export PUBLIC_URL="true"

# Start the public application
echo "Starting public app on port 8080..."
python one_public_app.py