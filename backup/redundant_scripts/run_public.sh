#!/bin/bash
# Public deployment script for NOUS Personal Assistant

echo "🚀 Starting NOUS Public Assistant..."

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

# Start the application
echo "🌐 Starting web server on port 8080..."
python nous_public.py