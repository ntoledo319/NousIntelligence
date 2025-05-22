#!/bin/bash
# Clean startup script for NOUS Personal Assistant

echo "Starting clean NOUS application..."

# Create required directories
mkdir -p static templates logs

# Set environment variables
export PORT=8080
export FLASK_ENV=production

# Generate a secret key if it doesn't exist
if [ ! -f ".secret_key" ]; then
    echo "Generating new secret key..."
    python -c "import secrets; print(secrets.token_hex(24))" > .secret_key
    chmod 600 .secret_key
fi

# Set secret key
export SECRET_KEY=$(cat .secret_key)

# Run the application
echo "Starting clean web server on port 8080..."
python app_clean.py