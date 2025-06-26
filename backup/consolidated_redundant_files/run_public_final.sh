#!/bin/bash

# NOUS Personal Assistant - Public Access Runner
# This script runs the public version of NOUS without Replit login requirement

echo "======= NOUS Public Access ======="
echo "Starting at $(date)"

# Create required directories
mkdir -p static templates logs flask_session instance

# Set environment variables for public access
export PORT=8080
export PYTHONUNBUFFERED=1
export PUBLIC_ACCESS=true

# Display startup information
echo "Starting NOUS Public Application on port 8080..."
echo "This version is publicly accessible without Replit login"
echo "Internal Google authentication is maintained for protected routes"

# Run the application
python app_public_final.py