#!/bin/bash

echo "Starting NOUS Personal Assistant (Simplified Version)"
echo "Starting at $(date)"

# Set up environment variables
export PORT=${PORT:-8080}
export FLASK_APP=app_simple.py
export FLASK_ENV=${FLASK_ENV:-production}
export PYTHONUNBUFFERED=1

# Ensure required directories exist
mkdir -p static templates logs flask_session instance uploads

# Install dependencies
pip install --quiet -r requirements.txt

# Start the application using Python directly (more reliable for deployment)
python app_simple.py