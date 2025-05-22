
#!/bin/bash
# NOUS Personal Assistant - Production Deployment Script

echo "🚀 Starting NOUS Personal Assistant for Production Deployment..."

# Set environment variables
export FLASK_ENV=production
export PORT=8080

# Kill any existing processes on port 8080
pkill -f "python.*main.py" || true
fuser -k 8080/tcp 2>/dev/null || true

# Start with gunicorn to properly bind to the expected port
exec gunicorn "app:app" --bind 0.0.0.0:8080 --workers 2 --timeout 120
