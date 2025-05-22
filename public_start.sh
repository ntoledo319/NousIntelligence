
#!/bin/bash
# NOUS Personal Assistant - Production Deployment Script

echo "🚀 Starting NOUS Personal Assistant for Production Deployment..."

# Create required directories
mkdir -p static templates logs flask_session instance

# Generate a secret key if it doesn't exist
if [ ! -f ".secret_key" ]; then
    echo "🔑 Generating new secret key..."
    python -c "import secrets; print(secrets.token_hex(24))" > .secret_key
    chmod 600 .secret_key
fi

# Set environment variables
export FLASK_ENV=production
export PORT=8080
export PYTHONUNBUFFERED=1
export SECRET_KEY=$(cat .secret_key)

# Set up deployment logs
mkdir -p logs
TIMESTAMP=$(date +%Y%m%d)
echo "[$(date +'%Y-%m-%d %H:%M:%S')] INFO in deployment_logger: [STARTUP] Production application starting up" >> "logs/deployment_${TIMESTAMP}.log"

# Kill any existing processes on port 8080
pkill -f "python.*main.py" 2>/dev/null || true
pkill -f "gunicorn" 2>/dev/null || true
fuser -k 8080/tcp 2>/dev/null || true

# Start with gunicorn directly to ensure it works properly
echo "✅ Starting Gunicorn with production configuration"
echo "[$(date +'%Y-%m-%d %H:%M:%S')] INFO in deployment_logger: [STARTUP] Starting gunicorn" >> "logs/deployment_${TIMESTAMP}.log"

# Use full path to gunicorn to ensure we're using the right executable
GUNICORN_PATH=$(which gunicorn)
echo "Using gunicorn at: $GUNICORN_PATH" >> "logs/deployment_${TIMESTAMP}.log"

# Start with explicit gunicorn command using wsgi.py
exec $GUNICORN_PATH \
    --bind 0.0.0.0:8080 \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    "wsgi:app"
