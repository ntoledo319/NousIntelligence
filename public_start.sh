
#!/bin/bash

echo "======= NOUS Application Startup ======="
echo "Starting at $(date)"

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
  pip install --quiet -r requirements.txt
  touch .deps_installed
  echo "Dependencies installed successfully"
fi

# Cleanup any existing processes (but don't fail if none exist)
echo "Cleaning up existing processes..."
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "gunicorn.*app:app" 2>/dev/null || true

# Extra debug information
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Flask file exists: $([ -f "app.py" ] && echo "YES" || echo "NO")"

# Start the application
echo "Starting NOUS application on port $PORT..."

# For deployment troubleshooting, use a simple direct run first
if [ "$DEBUG_MODE" = "true" ]; then
  echo "Running in debug mode with direct Python execution"
  exec python app.py
else
  # Start with Gunicorn for production
  echo "Running with Gunicorn for production"
  exec gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers=2 \
    --threads=4 \
    --timeout=120 \
    --access-logfile=logs/access.log \
    --error-logfile=logs/error.log \
    --log-level=info \
    --capture-output \
    app:app
fi
