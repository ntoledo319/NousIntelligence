#!/bin/bash
# NOUS Personal Assistant - Deployment Initialization Script
# This script handles initialization tasks for deployment

set -e  # Exit on error

echo "🔧 Initializing NOUS Personal Assistant deployment..."

# Create required directories
mkdir -p static templates logs flask_session instance

# Check database connection
echo "🔍 Checking database connection..."
python -c "
import os
import sys
from sqlalchemy import create_engine, text

db_url = os.environ.get('DATABASE_URL')
if not db_url:
    print('❌ DATABASE_URL environment variable not set')
    sys.exit(1)

try:
    engine = create_engine(db_url)
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    sys.exit(1)
"

# Generate a secret key if it doesn't exist
if [ ! -f ".secret_key" ]; then
    echo "🔑 Generating new secret key..."
    python -c "import secrets; print(secrets.token_hex(24))" > .secret_key
    chmod 600 .secret_key
fi

# Set up logging configuration
echo "📝 Setting up logging configuration..."
mkdir -p logs
TIMESTAMP=$(date +%Y%m%d)
echo "[$(date +'%Y-%m-%d %H:%M:%S')] INFO in deployment_logger: [INIT] Deployment initialization started" >> "logs/deployment_${TIMESTAMP}.log"

# Check for required dependencies
echo "📦 Checking for required dependencies..."
python -m pip list | grep -q gunicorn || {
    echo "⚠️ Gunicorn not found, installing..."
    python -m pip install gunicorn
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] INFO in deployment_logger: [INIT] Installed gunicorn package" >> "logs/deployment_${TIMESTAMP}.log"
}

# Ensure static files are accessible
echo "🌐 Checking static files..."
if [ ! -f "static/favicon.ico" ]; then
    echo "⚠️ Static files may be missing."
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] WARNING in deployment_logger: [INIT] Static files check failed" >> "logs/deployment_${TIMESTAMP}.log"
fi

# Initialize database if needed
echo "🗄️ Checking database initialization..."
python -c "
import os
import sys
from sqlalchemy import create_engine, text, inspect

db_url = os.environ.get('DATABASE_URL')
if not db_url:
    sys.exit(1)

try:
    engine = create_engine(db_url)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    if len(tables) == 0:
        print('⚠️ Database appears to be empty. Please run migrations.')
    else:
        print(f'✅ Database initialized with {len(tables)} tables')
except Exception as e:
    print(f'❌ Database check failed: {e}')
    sys.exit(1)
"

# Set required environment variables
export SECRET_KEY=$(cat .secret_key)
export PORT=8080
export FLASK_ENV="production"
export PYTHONUNBUFFERED=1

echo "✅ Deployment initialization complete"
echo "[$(date +'%Y-%m-%d %H:%M:%S')] INFO in deployment_logger: [INIT] Deployment initialization completed successfully" >> "logs/deployment_${TIMESTAMP}.log"