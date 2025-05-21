#!/bin/bash

# Print startup message
echo "Starting NOUS Personal Assistant..."

# Environment variables
export FLASK_APP=main.py
export FLASK_ENV=production
export PORT=8080
export AUTO_CREATE_TABLES=true

# Create necessary directories
mkdir -p flask_session uploads logs instance

# Set proper permissions
chmod -R 777 flask_session uploads logs instance

# Ensure we have a secret key
if [ ! -f ".secret_key" ]; then
    echo "Generating new secret key..."
    python -c "import secrets; print(secrets.token_hex(24))" > .secret_key
    chmod 600 .secret_key
fi

# Check for database migrations
if [ -f "run_migrations.py" ]; then
    echo "Running database migrations..."
    python run_migrations.py
fi

# Start Flask application with Gunicorn for stability
echo "Starting application with Gunicorn..."
exec gunicorn --bind 0.0.0.0:8080 --workers 2 --threads 2 --timeout 120 main:app