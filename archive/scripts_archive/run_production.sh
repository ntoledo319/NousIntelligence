#!/bin/bash
# Clean Production Deployment Script

set -e
echo "🚀 NOUS Clean Production Deploy"

# Set optimal environment
export FLASK_ENV=production
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1
export WERKZEUG_RUN_MAIN=true

# Get port and host
PORT=${PORT:-8080}
HOST=${HOST:-0.0.0.0}

# Create directories (silent)
mkdir -p logs static templates flask_session instance 2>/dev/null || true

echo "📊 Starting NOUS on $HOST:$PORT"

# Use the best available startup method
if command -v gunicorn >/dev/null 2>&1 && [ -f "gunicorn.conf.py" ]; then
    echo "🔧 Using Gunicorn (recommended)"
    exec gunicorn --config gunicorn.conf.py app:app
elif [ -f "app_optimized.py" ]; then
    echo "🔧 Using optimized app"
    exec python -c "
from app_optimized import app
import os
app.run(host='$HOST', port=int('$PORT'), debug=False, threaded=True)
"
else
    echo "🔧 Using main.py"
    exec python main.py
fi
