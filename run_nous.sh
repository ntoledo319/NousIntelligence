#!/bin/bash
# Simple script to run NOUS application

export PORT=5000
export FLASK_APP=main.py
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo "Starting NOUS Personal Assistant on port 5000..."
python main.py