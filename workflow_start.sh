#!/bin/bash
# Workflow startup script for NOUS Personal Assistant

echo "🚀 Starting NOUS Personal Assistant Workflow..."

# Create required directories
mkdir -p static templates logs

# Generate a secret key if it doesn't exist
if [ ! -f ".secret_key" ]; then
    echo "🔑 Generating new secret key..."
    python -c "import secrets; print(secrets.token_hex(24))" > .secret_key
    chmod 600 .secret_key
fi

# Set secret key
export SECRET_KEY=$(cat .secret_key)

# Start the application with gunicorn for better performance
echo "🌐 Starting web server on port 8080..."
python -m gunicorn 'app_clean:app' --bind '0.0.0.0:8080' --access-logfile - --error-logfile -