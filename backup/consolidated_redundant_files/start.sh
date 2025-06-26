#!/bin/bash

# NOUS Personal Assistant Startup Script
# Simple script for reliable deployment

echo "======= Starting NOUS Personal Assistant ======="
echo "Starting at $(date)"

# Create required directories
mkdir -p static templates logs flask_session instance

# Set environment variables
export PORT=8080
export PYTHONUNBUFFERED=1
export PUBLIC_ACCESS=true
export FLASK_APP=deployment.py

# Run the application directly
echo "Running deployment (public access, no Replit login)"
python deployment.py