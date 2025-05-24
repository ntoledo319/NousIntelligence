#!/bin/bash

# NOUS Personal Assistant - Public Deployment Script
# This script sets up a completely public application without login requirements

echo "======= NOUS Public Deployment Setup ======="
echo "Starting at $(date)"

# Create log directory
mkdir -p logs
LOGFILE="logs/public_deployment_$(date +%Y%m%d).log"
echo "$(date): Starting public deployment setup" > $LOGFILE

# Ensure all required directories exist
echo "Creating required directories..."
mkdir -p static templates logs flask_session instance uploads
echo "$(date): Directories created" >> $LOGFILE

# Clean up old and redundant files
echo "Cleaning up redundant files..."
rm -f public_app.py nous_deployment.py nous_app.py 2>/dev/null || true
echo "$(date): Redundant files cleaned" >> $LOGFILE

# Create a simple .replit.override file to ensure public access
echo "Creating public configuration override..."
cat > .replit.override << EOF
[auth]
pageEnabled = false
buttonEnabled = false
EOF
echo "$(date): Created public configuration override" >> $LOGFILE

# Ensure main app is correctly set up
echo "Configuring application for public access..."
export PUBLIC_MODE=true
export FLASK_APP=app.py
export FLASK_ENV=production
export PORT=8080
echo "$(date): Environment variables set" >> $LOGFILE

# Start the application
echo "Starting public application..."
exec python app.py