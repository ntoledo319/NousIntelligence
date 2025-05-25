#!/bin/bash

# NOUS Personal Assistant - Deployment Script
# Used with the deploy button

echo "======= NOUS Personal Assistant Deployment ======="
echo "Starting at $(date)"

# Create required directories
mkdir -p static templates logs flask_session instance

# Set environment variables
export PORT=8080
export PYTHONUNBUFFERED=1
export PUBLIC_ACCESS=true

# Start the application
echo "Starting NOUS application with public access (no Replit login required)"
python app_deploy.py