
#!/bin/bash

echo "======= NOUS Application Startup ======="

# Set up environment variables
export PORT=${PORT:-8080}
export FLASK_APP=app.py
export FLASK_ENV=${FLASK_ENV:-production}
export PUBLIC_MODE=true
export PYTHONUNBUFFERED=1

# Ensure required directories exist
mkdir -p static templates logs flask_session instance uploads

# Install dependencies if needed
if [ ! -f ".deps_installed" ] || [ "$REFRESH_DEPS" = "true" ]; then
  echo "Installing dependencies..."
  pip install -r requirements.txt
  touch .deps_installed
fi

# Cleanup any existing processes
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "gunicorn.*app:app" 2>/dev/null || true

# Start the application using Gunicorn
echo "Starting NOUS application on port $PORT..."
exec gunicorn \
  --bind 0.0.0.0:$PORT \
  --workers=2 \
  --threads=2 \
  --timeout=60 \
  --access-logfile=logs/access.log \
  --error-logfile=logs/error.log \
  --log-level=info \
  --preload \
  app:app
