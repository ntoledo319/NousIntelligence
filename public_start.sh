
#!/bin/bash
# NOUS Personal Assistant - Production Deployment Script

echo "🚀 Starting NOUS Personal Assistant for Production Deployment..."

# Set environment variables
export FLASK_ENV=production
export PORT=5000

# Start with gunicorn to properly bind to the expected port
exec gunicorn app_factory:app --bind 0.0.0.0:5000 --workers 2 --timeout 120
