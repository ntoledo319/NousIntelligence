#!/bin/bash
# NOUS Personal Assistant - Public Access Startup Script
# Optimized script for reliable deployment

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log_message "Starting NOUS Personal Assistant (Public Version)..."

# Create necessary directories
mkdir -p static
mkdir -p templates
mkdir -p templates/errors
mkdir -p logs
mkdir -p uploads
mkdir -p flask_session
mkdir -p instance

# Set environment variables
export PORT=${PORT:-8080}
export FLASK_ENV=production
export FLASK_APP=main.py
export REPLIT_ENVIRONMENT=production
export SKIP_AUTH=true

# Generate a secret key if none exists
if [ ! -f ".secret_key" ]; then
    log_message "Generating new secret key..."
    python -c "import secrets; print(secrets.token_hex(24))" > .secret_key
    chmod 600 .secret_key
fi

# Load secret key
export SECRET_KEY=$(cat .secret_key)
export SESSION_SECRET=$(cat .secret_key)

# Check database connection
log_message "Testing database connection..."
python -c "
import os
import sys
import psycopg2
try:
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    conn.close()
    print('Database connection successful')
except Exception as e:
    print(f'Warning: Database connection failed: {str(e)}', file=sys.stderr)
" || log_message "Database connection test failed, but continuing startup"

# Start the application
log_message "Starting web server on port $PORT..."
if command -v gunicorn &> /dev/null; then
    exec gunicorn -b 0.0.0.0:$PORT --access-logfile - main:app
else
    log_message "Gunicorn not found, using Flask development server..."
    exec python main.py
fi