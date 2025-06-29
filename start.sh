#!/bin/bash

# Start script for NOUS application
# This script is called by .replit configuration

echo "🚀 Starting NOUS application..."

# Set environment variables for production
export PORT=8080
export HOST=0.0.0.0
export FLASK_ENV=production
export FAST_STARTUP=true
export DISABLE_HEAVY_FEATURES=true

# Create necessary directories
mkdir -p logs static templates flask_session instance

# Kill any existing processes
pkill -f "python.*main.py" || true
pkill -f "python.*app.py" || true

# Start the application
echo "⚡ Starting with fast startup mode..."
python main.py