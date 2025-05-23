#!/bin/bash
# NOUS Personal Assistant - Simplified Deployment Script
# This script handles initialization and deployment in one step

# Create required directories
mkdir -p static templates logs flask_session instance

# Setup logging
TIMESTAMP=$(date +%Y%m%d)
LOG_FILE="logs/deployment_${TIMESTAMP}.log"

log_message() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
  echo "$1"
}

log_message "INFO: Starting NOUS deployment"

# Check database connection
log_message "INFO: Checking database connection"
python -c "
import os
import sys
from sqlalchemy import create_engine, text

db_url = os.environ.get('DATABASE_URL')
if not db_url:
    print('ERROR: DATABASE_URL environment variable not set')
    sys.exit(1)

try:
    engine = create_engine(db_url)
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('SUCCESS: Database connection successful')
except Exception as e:
    print(f'ERROR: Database connection failed: {e}')
    sys.exit(1)
"

# Generate a secret key if it doesn't exist
if [ ! -f ".secret_key" ]; then
    log_message "INFO: Generating new secret key"
    python -c "import secrets; print(secrets.token_hex(24))" > .secret_key
    chmod 600 .secret_key
fi

# Set required environment variables
export SECRET_KEY=$(cat .secret_key)
export PORT=${PORT:-8080}
export FLASK_APP=wsgi.py
export FLASK_ENV=production

# Install gunicorn if needed
if ! command -v gunicorn &> /dev/null; then
    log_message "INFO: Installing gunicorn"
    pip install gunicorn
fi

# Kill any existing processes on the port
log_message "INFO: Stopping any processes using port $PORT"
fuser -k $PORT/tcp 2>/dev/null || true

# Start the application with gunicorn
log_message "INFO: Starting application with gunicorn"
exec gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    wsgi:app