#!/bin/bash

# NOUS Personal Assistant - Final Public Deployment Script
# This script creates all needed files for public deployment

echo "======= NOUS Final Public Deployment ======="
echo "Starting at $(date)"

# Create required directories
mkdir -p static templates logs instance flask_session uploads

# Write a public .replit file (this is the key file)
cat > .replit << EOF
run = ["bash", "start_app.sh"]

[deployment]
run = ["bash", "start_app.sh"]
deploymentTarget = "cloudrun"

[env]
PORT = "8080"
FLASK_APP = "app.py"
FLASK_ENV = "production"
PYTHONUNBUFFERED = "1"

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

# Create a simple starter script
cat > start_app.sh << EOF
#!/bin/bash
# Start the NOUS application
export PORT=8080
export FLASK_APP=app.py
export FLASK_ENV=production
export PYTHONUNBUFFERED=1

# Create required directories
mkdir -p static templates logs instance flask_session uploads

# Start the application
python app.py
EOF

# Make it executable
chmod +x start_app.sh

# Start the application
echo "Starting the application..."
./start_app.sh