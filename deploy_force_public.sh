#!/bin/bash

# NOUS Personal Assistant - Force Public Deployment
# This script forcibly configures the app to be publicly accessible

echo "======= NOUS Force Public Deployment ======="
echo "Starting at $(date)"

# Create log directory
mkdir -p logs
LOGFILE="logs/force_public_$(date +%Y%m%d).log"
echo "Force public deployment started at $(date)" > "$LOGFILE"

# Create all required directories
mkdir -p static templates logs flask_session instance uploads
echo "$(date): Created required directories" >> "$LOGFILE"

# Directly create proper replit.nix file
echo "Creating optimized replit.nix..."
cat > replit.nix << EOF
{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.flask
    pkgs.python311Packages.psutil
    pkgs.python311Packages.requests
    pkgs.python311Packages.werkzeug
    pkgs.python311Packages.gunicorn
    pkgs.python311Packages.sqlalchemy
    pkgs.python311Packages.psycopg2
  ];
}
EOF
echo "$(date): Created replit.nix" >> "$LOGFILE"

# Create the proper .replit file
echo "Creating public .replit file..."
cat > .replit << EOF
run = ["bash", "run_public.sh"]

modules = ["python-3.11", "postgresql-16"]

[nix]
channel = "stable-24_05"

[deployment]
run = ["bash", "run_public.sh"]
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
echo "$(date): Created .replit" >> "$LOGFILE"

# Create a minimal run script
echo "Creating public runner script..."
cat > run_public.sh << EOF
#!/bin/bash

# NOUS Personal Assistant - Public Runner

# Set environment variables
export PORT=8080
export FLASK_APP=app.py
export FLASK_ENV=production
export PYTHONUNBUFFERED=1

# Create required directories
mkdir -p static templates logs instance flask_session uploads

# Clean up any existing processes
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "gunicorn.*app:app" 2>/dev/null || true

# Start the application
echo "Starting public NOUS application..."
exec python app.py
EOF
chmod +x run_public.sh
echo "$(date): Created and made executable run_public.sh" >> "$LOGFILE"

# Run the public start script
echo "Starting public application..."
bash run_public.sh &
echo "$(date): Started public application" >> "$LOGFILE"

echo "======= Force Public Deployment Complete ======="
echo "Your app should now be publicly accessible without requiring Replit login"
echo "Deployment completed at $(date)" >> "$LOGFILE"
echo "When deploying, use 'bash run_public.sh' as your run command"