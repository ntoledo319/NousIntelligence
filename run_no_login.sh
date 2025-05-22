#!/bin/bash
# Run NOUS Personal Assistant without requiring login

# Set environment variables
export FLASK_APP=nous_public.py
export FLASK_ENV=development
export PORT=8080

# Start the application
echo "Starting NOUS Personal Assistant (No Login Required)"
echo "===================================================="
python nous_public.py