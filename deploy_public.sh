#!/bin/bash

# NOUS Personal Assistant - Public Deployment Script
# This script prepares and deploys the NOUS application with public access

echo "======= NOUS Public Deployment ======="
echo "Starting public deployment at $(date)"

# Create deployment log
mkdir -p logs
DEPLOY_LOG="logs/public_deployment_$(date +%Y%m%d).log"
echo "Public deployment started at $(date)" > "$DEPLOY_LOG"

# Ensure required directories exist
echo "Creating required directories..."
mkdir -p static templates logs flask_session instance uploads
echo "$(date): Directories created" >> "$DEPLOY_LOG"

# Clean up old sessions and temporary files
echo "Cleaning up temporary files..."
find flask_session -type f -mtime +7 -delete 2>/dev/null || true
find logs -name "*.log" -type f -mtime +30 -delete 2>/dev/null || true
echo "$(date): Temporary files cleaned" >> "$DEPLOY_LOG"

# Copy public deployment configuration
echo "Setting up public deployment configuration..."
cp public_deployment.toml replit.toml
echo "$(date): Public configuration applied" >> "$DEPLOY_LOG"

# Ensure permissions are correct
chmod +x public_start.sh
chmod +x health_check.sh
echo "$(date): Permissions updated" >> "$DEPLOY_LOG"

# Verify static files
if [ ! -f "static/styles.css" ]; then
    echo "Creating styles.css..."
    echo "/* NOUS Personal Assistant Styles */" > static/styles.css
    echo "body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; }" >> static/styles.css
    echo "$(date): Created basic styles.css" >> "$DEPLOY_LOG"
fi

# Cleanup any existing processes
echo "Cleaning up existing processes..."
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "gunicorn.*app:app" 2>/dev/null || true
echo "$(date): Process cleanup completed" >> "$DEPLOY_LOG"

# Start the application with public access
echo "Starting the NOUS application with public access..."
export PUBLIC_MODE=true
export FLASK_ENV=production
bash public_start.sh &
PID=$!
echo "$(date): Public application started with PID $PID" >> "$DEPLOY_LOG"

# Wait a bit for the application to start
sleep 5

# Check if the application is running
if ps -p $PID > /dev/null; then
    echo "Public application started successfully!"
    echo "$(date): Public application confirmed running" >> "$DEPLOY_LOG"
else
    echo "WARNING: Application may not have started correctly"
    echo "$(date): Application start verification failed" >> "$DEPLOY_LOG"
fi

# Start health monitoring in the background
echo "Starting health monitoring..."
nohup ./health_check.sh > logs/health_check.log 2>&1 &
HEALTH_PID=$!
echo "$(date): Health monitoring started with PID $HEALTH_PID" >> "$DEPLOY_LOG"

echo "======= Public Deployment Complete ======="
echo "NOUS Application should be running at http://localhost:8080"
echo "Your application should now be publicly accessible without login"
echo "Deployment completed at $(date)" >> "$DEPLOY_LOG"