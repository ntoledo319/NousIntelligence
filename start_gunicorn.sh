#!/bin/bash

# NOUS Personal Assistant - Gunicorn Startup Script
# This script ensures the app starts with Gunicorn for proper Replit compatibility

echo "=== NOUS Personal Assistant ==="
echo "Starting with Gunicorn for reliable deployment..."

# Kill any existing processes
pkill -f "python" 2>/dev/null || true
pkill -f "gunicorn" 2>/dev/null || true

# Clear port 8080 (used by Replit)
fuser -k 8080/tcp 2>/dev/null || true

# Start with gunicorn
python -m gunicorn nous_solution:app -b 0.0.0.0:8080 --log-level info