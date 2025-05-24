
#!/bin/bash

echo "======= NOUS Application Startup ======="
echo "Starting at $(date)"

# Set up environment variables
export PORT=${PORT:-8080}
export FLASK_APP=app.py
export FLASK_ENV=${FLASK_ENV:-production}
export PUBLIC_MODE=true
export PYTHONUNBUFFERED=1

# Create log entry for deployment tracking
mkdir -p logs
LOGFILE="logs/deployment_$(date +%Y%m%d).log"
echo "$(date): Starting deployment" >> $LOGFILE

# Ensure required directories exist
echo "Creating required directories..."
mkdir -p static templates logs flask_session instance uploads
echo "$(date): Directories verified" >> $LOGFILE

# Cleanup any existing processes (but don't fail if none exist)
echo "Cleaning up existing processes..."
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "gunicorn.*app:app" 2>/dev/null || true
echo "$(date): Process cleanup completed" >> $LOGFILE

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
" >> $LOGFILE 2>&1

if [ $? -ne 0 ]; then
    echo "WARNING: Database connectivity check failed - see $LOGFILE for details"
    echo "$(date): Database connectivity check FAILED" >> $LOGFILE
else
    echo "Database connectivity verified"
    echo "$(date): Database connectivity verified" >> $LOGFILE
fi

# Verify static files exist
if [ ! -f "static/styles.css" ]; then
    echo "WARNING: Missing static files"
    echo "$(date): Missing static files" >> $LOGFILE
else
    echo "Static files verified"
    echo "$(date): Static files verified" >> $LOGFILE
fi

# Extra debug information
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Flask file exists: $([ -f "app.py" ] && echo "YES" || echo "NO")"
echo "$(date): Environment check completed" >> $LOGFILE

# Start the application
echo "Starting NOUS application on port $PORT..."
echo "$(date): Application starting on port $PORT" >> $LOGFILE

# For deployment troubleshooting, use a simple direct run first
if [ "$DEBUG_MODE" = "true" ]; then
    echo "Running in debug mode with direct Python execution"
    echo "$(date): Starting in DEBUG mode" >> $LOGFILE
    exec python app.py
else
    # Start with Gunicorn for production
    echo "Running with Gunicorn for production"
    echo "$(date): Starting with Gunicorn" >> $LOGFILE
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
fi
