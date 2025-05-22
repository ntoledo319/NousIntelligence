
#!/bin/bash
# NOUS Personal Assistant - Production Deployment Script

echo "🚀 Starting NOUS Personal Assistant for Production Deployment..."

# Set environment variables
export FLASK_ENV=production
export PORT=5000

# Kill any existing processes on port 5000
pkill -f "python.*main.py" || true
fuser -k 5000/tcp 2>/dev/null || true

# Start with gunicorn to properly bind to the expected port
exec gunicorn "app_factory:create_app()" --bind 0.0.0.0:5000 --workers 2 --timeout 120
