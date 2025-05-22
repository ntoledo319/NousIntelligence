#!/bin/bash
# NOUS Personal Assistant - Deployment Fix Script

echo "🔧 Running deployment fixes for NOUS Personal Assistant..."

# Ensure all required directories exist
mkdir -p static templates logs flask_session instance

# Fix permissions for critical directories
chmod -R 755 static templates
chmod -R 777 logs flask_session instance

# Ensure the virtual environment is properly set up
if [ -d ".venv" ]; then
    echo "✅ Virtual environment found"
else
    echo "🔄 Setting up Python environment"
    python -m venv .venv
fi

# Generate a secret key if it doesn't exist
if [ ! -f ".secret_key" ]; then
    echo "🔑 Generating new secret key..."
    python -c "import secrets; print(secrets.token_hex(24))" > .secret_key
    chmod 600 .secret_key
fi

# Update environment variables
export SECRET_KEY=$(cat .secret_key)
export FLASK_ENV="production"
export PORT=8080

# Log the fix completion
echo "[$(date +'%Y-%m-%d %H:%M:%S')] INFO in deployment_logger: [FIX] Deployment fixes applied" >> "logs/deployment_$(date +%Y%m%d).log"

echo "✅ Deployment fixes complete. You can now deploy your application."