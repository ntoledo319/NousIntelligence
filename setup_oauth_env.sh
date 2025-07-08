#!/bin/bash
# OAuth Setup Script for NOUS Intelligence

echo "Setting up OAuth environment variables..."

# Generate secure session secret
export SESSION_SECRET=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')

# Set your Google OAuth credentials here
export GOOGLE_CLIENT_ID="YOUR_CLIENT_ID.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="GOCSPX-YOUR_SECRET_HERE"

# Database URL (adjust as needed)
export DATABASE_URL="sqlite:///nous.db"

echo "Environment variables set!"
echo "SESSION_SECRET: ${SESSION_SECRET:0:10}... (truncated)"
echo "GOOGLE_CLIENT_ID: $GOOGLE_CLIENT_ID"
echo "GOOGLE_CLIENT_SECRET: ${GOOGLE_CLIENT_SECRET:0:10}... (truncated)"
echo "DATABASE_URL: $DATABASE_URL"

# Create .env file
cat > .env << EOF
SESSION_SECRET=$SESSION_SECRET
GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET=$GOOGLE_CLIENT_SECRET
DATABASE_URL=$DATABASE_URL
EOF

echo "Created .env file"
