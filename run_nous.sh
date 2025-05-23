#!/bin/bash

# NOUS Personal Assistant - Deployment Script
echo "Starting NOUS Personal Assistant..."

# Make sure the port environment variable is set
export PORT=3000
export FLASK_APP=new_app.py

# Run the application
python new_app.py