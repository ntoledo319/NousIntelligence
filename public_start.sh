
#!/bin/bash

# NOUS Personal Assistant - Deployment Script
echo "Starting NOUS Personal Assistant..."

# Ensure needed directories exist
mkdir -p static templates logs flask_session

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=production
export PORT=${PORT:-8080}
export PUBLIC_MODE=true

# Install dependencies if needed
if [ "$INSTALL_DEPS" = "true" ] || [ "$REFRESH_DEPS" = "true" ]; then
  echo "Installing dependencies..."
  pip install -r requirements.txt
  
  # Ensure markupsafe is properly installed (common issue)
  if ! pip show markupsafe > /dev/null; then
    echo "Installing markupsafe separately..."
    pip install --user markupsafe==2.1.5
  fi
fi

# Start the application using Gunicorn
echo "Starting application on port $PORT..."
exec gunicorn --bind 0.0.0.0:$PORT --workers=2 --threads=2 --timeout=60 app:app
