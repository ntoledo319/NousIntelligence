#!/bin/bash

# NOUS Personal Assistant - One App Deployment Script
# This script deploys the single consolidated public application

echo "======= NOUS One App Deployment ======="
echo "Starting deployment at $(date)"

# Create required directories and logs
mkdir -p logs static templates instance flask_session uploads
LOGFILE="logs/one_app_deployment_$(date +%Y%m%d).log"
echo "One App deployment started at $(date)" > "$LOGFILE"

# Clean up any redundant files and processes
echo "Cleaning up environment..."
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "gunicorn.*app:app" 2>/dev/null || true
echo "$(date): Environment cleaned" >> "$LOGFILE"

# Configure for public deployment
echo "Setting up public deployment configuration..."
cp replit_one_app.toml replit.toml
echo "$(date): Deployment configuration applied" >> "$LOGFILE"

# Ensure static files exist
if [ ! -f "static/styles.css" ]; then
    echo "Creating basic styles..."
    echo "/* NOUS Personal Assistant Styles */" > static/styles.css
    echo "body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }" >> static/styles.css
    echo "$(date): Created basic styles" >> "$LOGFILE"
fi

# Start the application
echo "Starting One App application..."
export PUBLIC_MODE=true
export FLASK_APP=one_app.py
export FLASK_ENV=production
export PORT=8080
export PYTHONUNBUFFERED=1

echo "$(date): Starting application with one_app.py" >> "$LOGFILE"
exec python one_app.py