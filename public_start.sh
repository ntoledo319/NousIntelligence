
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

# Install dependencies with pip (only if needed)
if [ "$INSTALL_DEPS" = "true" ]; then
  pip install -r requirements.txt
fi

# Start the application using Gunicorn
exec gunicorn --bind 0.0.0.0:$PORT --workers=2 --threads=2 --timeout=60 main:app
