#!/bin/bash

# NOUS Personal Assistant - Public Access Script
# This script ensures the application is publicly accessible without login requirements

echo "======= NOUS Public Access ======="
echo "Starting at $(date)"

# Create required directories
mkdir -p static templates logs

# Clean up any existing processes
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "python.*app_public.py" 2>/dev/null || true

# Set environment variables for public access
export PORT=8080
export PYTHONUNBUFFERED=1
export PUBLIC_ACCESS=true

# Start the application
echo "Starting public NOUS app on port 8080..."
python app_public.py