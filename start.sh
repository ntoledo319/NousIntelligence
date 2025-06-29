#!/bin/bash

# NOUS Application Startup Script
# Starts the application with proper configuration for Replit deployment

echo "🚀 Starting NOUS Application..."

# Set environment variables for optimal performance
export FLASK_ENV=production
export FLASK_DEBUG=false
export FAST_STARTUP=true
export DISABLE_HEAVY_FEATURES=true

# Ensure logs directory exists
mkdir -p logs

# Start the application
echo "✅ Starting Flask application on port 5000..."
python3 app.py

echo "🎯 NOUS Application started successfully"
echo "🌐 Access the app at http://localhost:5000"
echo "🚀 Demo mode available at /demo"
echo "❤️ Health check at /health"