
#!/bin/bash

# NOUS Personal Assistant - Public Deployment Script
echo "Starting NOUS Personal Assistant for public deployment..."

# Ensure needed directories exist
mkdir -p static/css static/js templates flask_session logs

# Set environment variables for public deployment
export FLASK_APP=main.py
export FLASK_ENV=production
export PORT=${PORT:-8080}
export PUBLIC_MODE=true

# Install dependencies with pip - attempt with user flag if regular install fails
if [ "$INSTALL_DEPS" = "true" ] || [ "$REFRESH_DEPS" = "true" ]; then
  echo "Installing dependencies..."
  pip install -r requirements.txt || pip install --user -r requirements.txt
  
  # Check if markupsafe is properly installed
  if ! pip show markupsafe > /dev/null; then
    echo "Attempting to fix markupsafe installation..."
    pip install --user markupsafe==2.1.5
  fi
fi

# Start the application using Gunicorn
exec gunicorn --bind 0.0.0.0:$PORT --workers=2 --threads=2 --timeout=60 main:app
