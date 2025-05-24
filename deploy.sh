#!/bin/bash

# NOUS Personal Assistant - Deployment Script
# This script prepares and deploys the NOUS application

echo "======= NOUS Application Deployment ======="
echo "Starting deployment at $(date)"

# Create deployment log
mkdir -p logs
DEPLOY_LOG="logs/deployment_$(date +%Y%m%d).log"
echo "Deployment started at $(date)" > "$DEPLOY_LOG"

# Ensure required directories exist
echo "Creating required directories..."
mkdir -p static templates logs flask_session instance uploads
echo "$(date): Directories created" >> "$DEPLOY_LOG"

# Clean up old sessions and temporary files
echo "Cleaning up temporary files..."
find flask_session -type f -mtime +7 -delete 2>/dev/null || true
find logs -name "*.log" -type f -mtime +30 -delete 2>/dev/null || true
echo "$(date): Temporary files cleaned" >> "$DEPLOY_LOG"

# Ensure permissions are correct
chmod +x public_start.sh
chmod +x health_check.sh
echo "$(date): Permissions updated" >> "$DEPLOY_LOG"

# Verify static files
if [ ! -f "static/styles.css" ]; then
    echo "WARNING: styles.css not found. Checking for backup..."
    echo "$(date): styles.css not found" >> "$DEPLOY_LOG"
    
    # Create styles.css if it doesn't exist
    if [ ! -d "static" ]; then
        mkdir -p static
    fi
    
    # Extract styles from layout.html if styles.css is missing
    echo "Creating styles.css from embedded styles..."
    sed -n '/<style>/,/<\/style>/p' templates/layout.html | \
        sed 's/<style>//' | sed 's/<\/style>//' > static/styles.css
    echo "$(date): Created styles.css from embedded styles" >> "$DEPLOY_LOG"
fi

# Verify database connectivity
echo "Verifying database connectivity..."
python -c "
import os
from sqlalchemy import create_engine, text
try:
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///instance/nous.db')
    engine = create_engine(db_url)
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('Database connection successful')
except Exception as e:
    print(f'Database connection error: {str(e)}')
    exit(1)
" >> "$DEPLOY_LOG" 2>&1

if [ $? -ne 0 ]; then
    echo "ERROR: Database connectivity failed, see $DEPLOY_LOG for details"
    echo "$(date): Database connectivity FAILED" >> "$DEPLOY_LOG"
    echo "Will continue with deployment using SQLite fallback"
else
    echo "Database connectivity verified"
    echo "$(date): Database connectivity verified" >> "$DEPLOY_LOG"
fi

# Check if application files exist
if [ ! -f "app.py" ]; then
    echo "ERROR: app.py not found!"
    echo "$(date): app.py not found" >> "$DEPLOY_LOG"
    exit 1
fi

if [ ! -f "main.py" ]; then
    echo "ERROR: main.py not found!"
    echo "$(date): main.py not found" >> "$DEPLOY_LOG"
    exit 1
fi

# Cleanup any existing processes
echo "Cleaning up existing processes..."
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "gunicorn.*app:app" 2>/dev/null || true
echo "$(date): Process cleanup completed" >> "$DEPLOY_LOG"

# Start the application
echo "Starting the NOUS application..."
bash public_start.sh &
PID=$!
echo "$(date): Application started with PID $PID" >> "$DEPLOY_LOG"

# Wait a bit for the application to start
sleep 5

# Check if the application is running
if ps -p $PID > /dev/null; then
    echo "Application started successfully!"
    echo "$(date): Application confirmed running" >> "$DEPLOY_LOG"
else
    echo "WARNING: Application may not have started correctly"
    echo "$(date): Application start verification failed" >> "$DEPLOY_LOG"
fi

# Start health monitoring in the background
echo "Starting health monitoring..."
nohup ./health_check.sh > logs/health_check.log 2>&1 &
HEALTH_PID=$!
echo "$(date): Health monitoring started with PID $HEALTH_PID" >> "$DEPLOY_LOG"

echo "======= Deployment Complete ======="
echo "NOUS Application should be running at http://localhost:8080"
echo "Health monitoring is active"
echo "Deployment completed at $(date)" >> "$DEPLOY_LOG"