#!/bin/bash
# NOUS Personal Assistant Application Startup Script
# This script sets up and starts the NOUS application with improved error handling and reliability

# Function to log messages with timestamp
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log_message "Starting NOUS Personal Assistant..."

# Error handling
set -e  # Exit immediately if a command exits with a non-zero status
trap 'log_message "Error occurred. Startup failed at line $LINENO"' ERR

# Create required directories if they don't exist
mkdir -p flask_session
mkdir -p uploads
mkdir -p logs
mkdir -p instance

# Set environment variables
export FLASK_APP=main.py

# Determine environment based on Replit's environment
if [ -n "$REPL_ID" ]; then
    log_message "Running in Replit environment"
    export FLASK_ENV=production
    export REPLIT_ENVIRONMENT=production
    export PORT=${PORT:-8080}
    
    # Set Replit-specific redirect URI if not already set
    if [ -z "$GOOGLE_REDIRECT_URI" ]; then
        # Use REPL_SLUG if available
        if [ -n "$REPL_SLUG" ]; then
            export GOOGLE_REDIRECT_URI="https://$REPL_SLUG.replit.app/callback/google"
            log_message "Set Google redirect URI to: $GOOGLE_REDIRECT_URI"
        else
            log_message "Warning: Could not determine Replit URL. Google authentication may not work."
        fi
    fi
    
    # Set Spotify redirect URI if not already set
    if [ -z "$SPOTIFY_REDIRECT_URI" ] && [ -n "$REPL_SLUG" ]; then
        export SPOTIFY_REDIRECT_URI="https://$REPL_SLUG.replit.app/callback/spotify"
        log_message "Set Spotify redirect URI to: $SPOTIFY_REDIRECT_URI"
    fi
else
    log_message "Running in local environment"
    export FLASK_ENV=development
    export PORT=${PORT:-5000}
fi

# Check permissions on session directory
chmod -R 777 flask_session
chmod -R 777 uploads
chmod -R 777 logs

# Ensure we have a secret key
if [ ! -f ".secret_key" ]; then
    log_message "Generating new secret key..."
    python -c "import secrets; print(secrets.token_hex(24))" > .secret_key
    chmod 600 .secret_key
fi

# Export the secret key as an environment variable
if [ -f ".secret_key" ]; then
    export SECRET_KEY=$(cat .secret_key)
    export SESSION_SECRET=$(cat .secret_key)
    log_message "Secret key loaded from file"
fi

# Verify critical environment variables
if [ -z "$DATABASE_URL" ]; then
    log_message "ERROR: DATABASE_URL is not set. Application may not function correctly."
fi

if [ -z "$SECRET_KEY" ] && [ -z "$SESSION_SECRET" ]; then
    log_message "ERROR: Neither SECRET_KEY nor SESSION_SECRET is set. Application may not function correctly."
fi

# Check if database is accessible
log_message "Checking database connection..."
python -c "import os, sys, psycopg2; 
try: 
    conn = psycopg2.connect(os.environ.get('DATABASE_URL')); 
    conn.close(); 
    print('Database connection successful')
except Exception as e: 
    print(f'Warning: Database connection failed: {str(e)}', file=sys.stderr); 
    # Continue despite error
" || log_message "Database connection test failed, but continuing startup"

# Run deployment recovery checks first
if [ -f "deployment_recovery.py" ]; then
    log_message "Running deployment recovery checks..."
    python deployment_recovery.py --fix-all || log_message "Warning: Some deployment issues could not be automatically fixed"
fi

# Run database migrations if needed
if [ -f "run_migrations.py" ]; then
    log_message "Running database migrations..."
    python run_migrations.py || log_message "Warning: Database migrations reported errors, but continuing startup"
fi

# Start application
if [ "$FLASK_ENV" = "production" ]; then
    log_message "Starting application in production mode on port $PORT..."
    exec gunicorn -c gunicorn_config.py main:app
else
    log_message "Starting application in development mode on port $PORT..."
    exec python main.py
fi