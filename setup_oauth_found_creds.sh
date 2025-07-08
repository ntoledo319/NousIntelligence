#!/bin/bash
# OAuth Setup Script with Found Credentials
# These credentials were discovered in your system files

echo "🔐 Setting up OAuth with credentials found in your system..."

# OAuth credentials from security_fixes_backup/phase2_backup_20250701_064833/archive_backup/operation_public_or_bust_final.py
export GOOGLE_CLIENT_ID='1015094007473-337qm1ofr5htlodjmsf2p6r3fcht6pg2.apps.googleusercontent.com'
export GOOGLE_CLIENT_SECRET='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'

# Generate secure session secret
export SESSION_SECRET=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')

# Database URL
export DATABASE_URL='sqlite:///nous.db'

# Development settings
export FLASK_DEBUG=true
export FLASK_ENV=development
export PORT=8080

echo "✅ Environment variables set!"
echo ""
echo "📋 Configuration:"
echo "   GOOGLE_CLIENT_ID: ${GOOGLE_CLIENT_ID:0:50}..."
echo "   GOOGLE_CLIENT_SECRET: ${GOOGLE_CLIENT_SECRET:0:20}..."
echo "   SESSION_SECRET: ${SESSION_SECRET:0:20}... (generated)"
echo "   DATABASE_URL: $DATABASE_URL"
echo ""
echo "🔍 Testing OAuth configuration..."
python3 -c "
import os
import sys
sys.path.insert(0, '.')
try:
    from utils.google_oauth import oauth_service
    if oauth_service.is_configured():
        print('✅ OAuth service is configured and ready!')
    else:
        print('⚠️  OAuth service initialization failed')
except Exception as e:
    print(f'❌ Error testing OAuth: {e}')
"

echo ""
echo "📝 Next steps:"
echo "1. Make sure these redirect URIs are in Google Cloud Console:"
echo "   • http://localhost:8080/auth/google/callback"
echo "   • https://your-app.replit.app/auth/google/callback"
echo ""
echo "2. To make these environment variables permanent, add to your shell profile:"
echo "   echo 'source $(pwd)/setup_oauth_found_creds.sh' >> ~/.zshrc"
echo ""
echo "3. Run your application:"
echo "   python3 app.py" 