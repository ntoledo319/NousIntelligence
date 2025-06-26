#!/bin/bash

# NOUS Personal Assistant - Main Runner
# This script ensures public access with no login requirements

echo "======= NOUS Application Runner ======="
echo "Starting at $(date)"

# Create required directories
mkdir -p static templates logs

# Set environment variables for public access
export PORT=8080
export PYTHONUNBUFFERED=1
export PUBLIC_URL="true"

# Start the public application
echo "Starting NOUS on port 8080..."
python public_app.py