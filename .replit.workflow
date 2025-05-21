#!/bin/bash

# Print startup message
echo "Starting NOUS Personal Assistant..."

# Create required directories
mkdir -p flask_session uploads logs instance

# Set proper permissions
chmod -R 777 flask_session uploads logs

# Ensure we have a secret key
if [ ! -f ".secret_key" ]; then
    echo "Generating new secret key..."
    python -c "import secrets; print(secrets.token_hex(24))" > .secret_key
    chmod 600 .secret_key
fi

# Set environment variables
export FLASK_APP=main.py
export FLASK_ENV=production
export PORT=8080
export SESSION_TYPE=filesystem

# Check if database is accessible
python -c "import os, psycopg2; conn = psycopg2.connect(os.environ.get('DATABASE_URL')); conn.close()" || {
    echo "Warning: Database connection failed, application may not function correctly"
    # Continue anyway, as the application should handle DB errors gracefully
}

# Run database migrations if needed
if [ -f "run_migrations.py" ]; then
    echo "Running database migrations..."
    python run_migrations.py
fi

# Launch the application using Gunicorn for better reliability
echo "Starting application with Gunicorn..."
exec gunicorn -c gunicorn_config.py main:app