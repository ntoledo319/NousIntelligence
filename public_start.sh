
#!/bin/bash

echo "======= NOUS Application Startup ======="

# Set default port
export PORT=${PORT:-8080}

# Ensure required directories exist
mkdir -p static templates logs flask_session instance

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=production
export PUBLIC_MODE=true

# Install dependencies if needed
if [ ! -f ".deps_installed" ] || [ "$REFRESH_DEPS" = "true" ]; then
  echo "Installing dependencies..."
  pip install -r requirements.txt
  touch .deps_installed
fi

# Start the application using Gunicorn
echo "Starting application on port $PORT..."
exec gunicorn --bind 0.0.0.0:$PORT --workers=2 --threads=2 --timeout=60 app:app
