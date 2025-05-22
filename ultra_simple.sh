#!/bin/bash
# Ultra-simple single-file execution script

echo "Starting minimal NOUS application..."

# Create required directories
mkdir -p static templates logs

# Set environment variables
export PORT=8080
export FLASK_APP=minimal.py

# Run the application
echo "Starting minimal web server on port 8080..."
python minimal.py