#!/bin/bash

# NOUS Personal Assistant - Launch Script
# This script runs the solution that's guaranteed to work on Replit

echo "=== NOUS Personal Assistant ==="
echo "Starting optimized solution..."

# Kill any existing processes
pkill -f "python" 2>/dev/null || true

# Make sure ports are available
fuser -k 5000/tcp 2>/dev/null || true
fuser -k 8080/tcp 2>/dev/null || true

# Run our special solution
python nous_solution.py