#!/bin/bash
# NOUS Personal Assistant Application Startup Script
# This script sets up and starts the NOUS application

echo "Starting NOUS Personal Assistant..."

# Create required directories if they don't exist
mkdir -p flask_session
mkdir -p uploads
mkdir -p logs
mkdir -p instance

# Set environment variables
export FLASK_APP=main.py

# Determine environment based on Replit's environment
if [ -n "$REPL_ID" ]; then
    echo "Running in Replit environment"
    export FLASK_ENV=production
    export REPLIT_ENVIRONMENT=production
    export PORT=${PORT:-8080}
    
    # Set Replit-specific redirect URI if not already set
    if [ -z "$GOOGLE_REDIRECT_URI" ]; then
        # Use REPL_SLUG if available
        if [ -n "$REPL_SLUG" ]; then
            export GOOGLE_REDIRECT_URI="https://$REPL_SLUG.replit.app/callback/google"
            echo "Set Google redirect URI to: $GOOGLE_REDIRECT_URI"
        else
            echo "Warning: Could not determine Replit URL. Google authentication may not work."
        fi
    fi
else
    echo "Running in local environment"
    export FLASK_ENV=development
    export PORT=${PORT:-5000}
fi

# Check permissions on session directory
chmod -R 777 flask_session
chmod -R 777 uploads

# Ensure we have a secret key
if [ ! -f ".secret_key" ]; then
    echo "Generating new secret key..."
    python -c "import secrets; print(secrets.token_hex(24))" > .secret_key
    chmod 600 .secret_key
fi

# Run database migrations if needed
if [ -f "run_migrations.py" ]; then
    echo "Checking for database migrations..."
    python run_migrations.py
fi

# Install required packages if needed
if [ -f "requirements.txt" ]; then
    echo "Installing required packages..."
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# Start application
if [ "$FLASK_ENV" = "production" ]; then
    echo "Starting application in production mode on port $PORT..."
    gunicorn -c gunicorn_config.py main:app
else
    echo "Starting application in development mode on port $PORT..."
    python main.py
fi