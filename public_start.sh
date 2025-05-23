#!/bin/bash
# NOUS Personal Assistant - Public Workflow Startup Script

# Create required directories
mkdir -p static templates logs flask_session instance uploads/voice

# Setup logging
TIMESTAMP=$(date +%Y%m%d)
LOG_FILE="logs/deployment_${TIMESTAMP}.log"

log_message() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
  echo "$1"
}

log_message "INFO: Starting NOUS Personal Assistant (Public Mode)"

# Generate a secret key if it doesn't exist
if [ ! -f ".secret_key" ]; then
    log_message "INFO: Generating new secret key"
    python -c "import secrets; print(secrets.token_hex(24))" > .secret_key
    chmod 600 .secret_key
fi

# Set environment variables for public access
export SECRET_KEY=$(cat .secret_key)
export PORT=8080
export FLASK_APP=main.py
export FLASK_ENV=production
export PYTHONUNBUFFERED=1
export PUBLIC_ACCESS=true

# Clean up any existing processes
log_message "INFO: Cleaning up any existing processes"
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "python.*main.py" 2>/dev/null || true
pkill -f "gunicorn" 2>/dev/null || true
fuser -k 8080/tcp 2>/dev/null || true

# Start the Flask application
log_message "INFO: Starting Flask application in public mode"
python main.py