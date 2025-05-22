#!/bin/bash

# NOUS Personal Assistant - Main Workflow Script
# This script runs the NOUS app with proper port configuration

# Ensure clean start
pkill -f "python" 2>/dev/null || true
fuser -k 8080/tcp 2>/dev/null || true

# Start the application
echo "Starting NOUS Personal Assistant..."
exec python app.py

