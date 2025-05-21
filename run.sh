#!/bin/bash
# Quick run script for local development

export FLASK_APP=main.py
export FLASK_ENV=development
export PORT=5000

# Create directories if they don't exist
mkdir -p flask_session uploads logs instance

# Install requirements if needed
pip install -r requirements.txt

# Run the application in debug mode
python main.py 