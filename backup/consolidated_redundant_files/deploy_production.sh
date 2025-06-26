#!/bin/bash

# NOUS Personal Assistant - Production Deployment Script
# This script prepares and deploys the NOUS application in production mode

echo "======= NOUS Production Deployment ======="
echo "Starting production deployment at $(date)"

# Create deployment log
mkdir -p logs
DEPLOY_LOG="logs/production_deployment_$(date +%Y%m%d).log"
echo "Production deployment started at $(date)" > "$DEPLOY_LOG"

# Set production environment variables
export FLASK_ENV=production
export FLASK_APP=app.py
export PORT=8080
export PUBLIC_MODE=true
export PYTHONUNBUFFERED=1

echo "$(date): Setting production environment variables" >> "$DEPLOY_LOG"

# Ensure required directories exist
echo "Creating required directories..."
mkdir -p static templates logs flask_session instance uploads
echo "$(date): Directories created" >> "$DEPLOY_LOG"

# Clean up old sessions and temporary files
echo "Cleaning up temporary files..."
find flask_session -type f -mtime +7 -delete 2>/dev/null || true
find logs -name "*.log" -type f -mtime +30 -delete 2>/dev/null || true
echo "$(date): Temporary files cleaned" >> "$DEPLOY_LOG"

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

# Cleanup any existing processes
echo "Cleaning up existing processes..."
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "gunicorn.*app:app" 2>/dev/null || true
echo "$(date): Process cleanup completed" >> "$DEPLOY_LOG"

# Start the application with Gunicorn (production mode)
echo "Starting the NOUS application in production mode..."
echo "$(date): Starting with Gunicorn" >> "$DEPLOY_LOG"

# Use Gunicorn for production deployment
exec gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers=2 \
    --threads=4 \
    --timeout=120 \
    --access-logfile=logs/access.log \
    --error-logfile=logs/error.log \
    --log-level=info \
    --capture-output \
    --preload \
    app:app