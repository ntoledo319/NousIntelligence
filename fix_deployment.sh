
#!/bin/bash

echo "======= NOUS Deployment Troubleshooter ======="
echo "Checking for common deployment issues..."

# Check if PORT environment variable is set
if [ -z "$PORT" ]; then
  echo "Setting PORT to 8080..."
  export PORT=8080
fi

# Check for essential directories
mkdir -p static/css static/js templates flask_session logs

# Check if Poetry files exist and remove them to avoid conflicts
if [ -f "poetry.lock" ]; then
  echo "Removing poetry.lock to prevent conflicts..."
  rm -f poetry.lock
fi

# Attempt to fix the markupsafe issue
echo "Reinstalling markupsafe package..."
pip uninstall -y markupsafe || true
pip install --user markupsafe==2.1.5

# Install other dependencies
echo "Installing dependencies using pip..."
pip install -r requirements.txt

echo "Deployment troubleshooting complete."
echo "You can now run 'bash public_start.sh' to start the application."
