#!/usr/bin/env python3
"""
Update App Configuration for Production Security
"""

import re
from pathlib import Path

def update_app_config():
    """Update app.py to use comprehensive security configuration"""
    
    app_file = Path('app.py')
    if not app_file.exists():
        print("app.py not found")
        return
    
    content = app_file.read_text()
    
    # Add import for security headers
    if 'from utils.security_middleware import init_security_headers' not in content:
        content = content.replace(
            'from utils.google_oauth import init_oauth, user_loader',
            'from utils.google_oauth import init_oauth, user_loader\nfrom utils.security_middleware import init_security_headers'
        )
    
    # Initialize security headers after app creation
    if 'init_security_headers(app)' not in content:
        content = content.replace(
            '    # Initialize database\n    try:',
            '    # Initialize security headers\n    init_security_headers(app)\n    \n    # Initialize database\n    try:'
        )
    
    # Update token encryption to use dedicated key
    content = content.replace(
        "os.environ.get('TOKEN_ENCRYPTION_KEY', os.environ.get('SESSION_SECRET', ''))",
        "os.environ.get('TOKEN_ENCRYPTION_KEY')"
    )
    
    # Save updated content
    app_file.write_text(content)
    print("Updated app.py with comprehensive security configuration")

def create_env_template():
    """Create comprehensive .env template"""
    
    env_content = """# NOUS Application Environment Configuration
# Copy to .env and fill in your values

# === CRITICAL SECURITY KEYS ===
# Generate using: python -c "from utils.secret_manager import generate_secure_secret; print(generate_secure_secret())"
SESSION_SECRET=  # Required: 64+ character secret for Flask sessions
TOKEN_ENCRYPTION_KEY=  # Required: Separate key for token encryption
API_SECRET_KEY=  # Required: Secret for API authentication

# === DATABASE ===
DATABASE_URL=postgresql://user:password@localhost/nous_db
DB_POOL_SIZE=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=300

# === GOOGLE OAUTH ===
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret

# === AI SERVICES ===
OPENAI_API_KEY=
GEMINI_API_KEY=
ANTHROPIC_API_KEY=

# === SECURITY SETTINGS ===
FLASK_ENV=production
DEBUG=false
CORS_ORIGINS=https://yourdomain.com
RATE_LIMIT_PER_MINUTE=60
MAX_CONTENT_LENGTH=10485760  # 10MB
SESSION_TIMEOUT=3600  # 1 hour
ACCOUNT_LOCKOUT_ATTEMPTS=5
ACCOUNT_LOCKOUT_DURATION=1800  # 30 minutes

# === MONITORING ===
SENTRY_DSN=
LOG_LEVEL=INFO
ENABLE_METRICS=true

# === FEATURE FLAGS ===
ENABLE_OAUTH=true
ENABLE_AI_FEATURES=true
ENABLE_ANALYTICS=true
ENABLE_NOTIFICATIONS=true
ENABLE_2FA=true
ENABLE_API_KEYS=true

# === DEPLOYMENT ===
PORT=8080
HOST=0.0.0.0
WORKERS=4
THREADS=2
"""
    
    Path('.env.production').write_text(env_content)
    print("Created .env.production template")

def create_deployment_config():
    """Create production deployment configuration"""
    
    nginx_config = """# NGINX Configuration for NOUS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
    limit_req_zone $binary_remote_addr zone=api:10m rate=60r/m;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    location /auth/ {
        limit_req zone=login burst=5 nodelay;
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api/ {
        limit_req zone=api burst=100 nodelay;
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Serve static files directly
    location /static/ {
        alias /home/nous/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
"""
    
    Path('nginx.conf').write_text(nginx_config)
    print("Created nginx.conf")

def main():
    print("Updating application configuration for production...")
    
    update_app_config()
    create_env_template()
    create_deployment_config()
    
    print("\nConfiguration updates complete!")
    print("\nNext steps:")
    print("1. Copy .env.production to .env and fill in your values")
    print("2. Generate secure secrets using the secret manager")
    print("3. Update nginx configuration with your domain")
    print("4. Run database migrations")
    print("5. Deploy to production")

if __name__ == '__main__':
    main()
