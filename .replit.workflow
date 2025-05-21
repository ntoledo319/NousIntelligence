#!/bin/bash

# Print startup message
echo "Starting NOUS Personal Assistant..."

# Create required directories
mkdir -p flask_session uploads logs

# Set proper permissions
chmod -R 777 flask_session uploads

# Environment variables
export FLASK_APP=main.py
export FLASK_ENV=production
export PORT=8080

# Launch the application using Flask development server
python -m flask run --host=0.0.0.0 --port=8080