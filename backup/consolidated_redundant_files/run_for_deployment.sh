#!/bin/bash

# NOUS Personal Assistant - Simplified Public Deployment Runner
# Use this as your deployment command

# Set environment variables
export PORT=8080
export FLASK_APP=app.py
export FLASK_ENV=production
export PYTHONUNBUFFERED=1
export PUBLIC_ACCESS=true

# Create required directories
mkdir -p static templates logs instance flask_session uploads

# Start the application
echo "Starting NOUS Personal Assistant in public mode..."
python app.py