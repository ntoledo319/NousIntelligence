#!/bin/bash

echo "Starting NOUS Personal Assistant (No Login Required)"
echo "===================================================="

# Export required environment variables
export PORT=8080
export FLASK_ENV=development
export FLASK_APP=app_simplified.py

# Run the simplified app without login requirements
python app_simplified.py