#!/bin/bash

# NOUS Personal Assistant - Public Deployment Script
# This script ensures the application is publicly accessible without login

echo "======= NOUS Public Deployment ======="
echo "Starting at $(date)"

# Create required directories
mkdir -p static templates logs

# Clean up any existing processes
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "python.*simple_app.py" 2>/dev/null || true

# Set environment variables for public access
export PORT=8080
export FLASK_APP=simple_app.py
export PYTHONUNBUFFERED=1
export PUBLIC_ACCESS=true

# Create a copy of the Replit configuration file for public access
cat > public_deploy_config.toml << 'EOF'
run = ["bash", "deploy_public.sh"]
entrypoint = "simple_app.py"

[env]
PYTHONUNBUFFERED = "1"
PUBLIC_ACCESS = "true"
PORT = "8080"

[deployment]
run = ["bash", "deploy_public.sh"]
deploymentTarget = "cloudrun"
publicDir = "/"
ignorePorts = false

[auth]
pageEnabled = false
buttonEnabled = false
EOF

echo "Starting public app on port 8080..."
python simple_app.py