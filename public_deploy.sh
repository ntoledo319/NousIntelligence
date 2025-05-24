#!/bin/bash

# NOUS Personal Assistant - Public Deployment Script
# This script deploys a completely public version with no login required

echo "======= NOUS Public Deployment ======="
echo "Starting public deployment at $(date)"

# Create required directories and logs
mkdir -p logs static templates instance flask_session uploads
LOGFILE="logs/public_deployment_$(date +%Y%m%d).log"
echo "Public deployment started at $(date)" > "$LOGFILE"

# Clean up any processes
echo "Cleaning up environment..."
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "gunicorn.*app:app" 2>/dev/null || true
echo "$(date): Environment cleaned" >> "$LOGFILE"

# Create .replit file directly for public deployment
echo "Configuring for public deployment..."
cat > .replit << EOF
run = ["bash", "run_public_app.sh"]

[deployment]
run = ["bash", "run_public_app.sh"]
deploymentTarget = "cloudrun"

[env]
PORT = "8080"
FLASK_APP = "one_app.py"
FLASK_ENV = "production"
PYTHONUNBUFFERED = "1"
PUBLIC_MODE = "true"

[server]
host = "0.0.0.0"
port = 8080

[[ports]]
localPort = 8080
externalPort = 80

[auth]
pageEnabled = false
buttonEnabled = false
EOF
echo "$(date): Public configuration created" >> "$LOGFILE"

# Start the public application
echo "Starting public application..."
export PUBLIC_MODE=true
export FLASK_APP=one_app.py
export FLASK_ENV=production

# Run the application
echo "$(date): Starting one_app.py" >> "$LOGFILE"
python one_app.py