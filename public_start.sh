
#!/bin/bash
# NOUS Personal Assistant - Production Deployment Script

echo "🚀 Starting NOUS Personal Assistant for Production Deployment..."

# Run initialization script for deployment
if [ -f "./deploy_init.sh" ]; then
    echo "Running deployment initialization..."
    chmod +x ./deploy_init.sh
    ./deploy_init.sh
else
    # Fallback if init script doesn't exist
    # Create required directories
    mkdir -p static templates logs flask_session instance

    # Generate a secret key if it doesn't exist
    if [ ! -f ".secret_key" ]; then
        echo "🔑 Generating new secret key..."
        python -c "import secrets; print(secrets.token_hex(24))" > .secret_key
        chmod 600 .secret_key
    fi
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

# Start with gunicorn using our configuration file for better production settings
echo "✅ Starting Gunicorn with production configuration"
exec gunicorn -c gunicorn_config.py "main:app"
