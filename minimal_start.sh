#!/bin/bash
# NOUS Personal Assistant - Minimal Startup Script
# This script starts a minimal version of the application for reliable deployment

echo "Starting NOUS Personal Assistant (Minimal Version)..."

# Set PORT environment variable if not already set
export PORT=${PORT:-8080}
export FLASK_ENV=${FLASK_ENV:-production}

# Start the minimal application
exec python app_minimal.py