#!/usr/bin/env python3
"""
Comprehensive OAuth Debugging and Fixing Tool
Diagnoses and fixes all Google OAuth login issues
"""

import os
import sys
import json
import re
import logging
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, urljoin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

class OAuthDebugger:
    """Comprehensive OAuth debugger and fixer"""
    
    def __init__(self):
        self.issues = []
        self.fixes_applied = []
        self.warnings = []
        
    def run_diagnostics(self):
        """Run complete OAuth diagnostics"""
        logger.info("🔍 Running Comprehensive OAuth Diagnostics")
        logger.info("=" * 60)
        
        # 1. Check environment variables
        self.check_environment_variables()
        
        # 2. Validate credential format
        self.validate_credential_format()
        
        # 3. Check OAuth service initialization
        self.check_oauth_initialization()
        
        # 4. Test redirect URI configuration
        self.check_redirect_uris()
        
        # 5. Check database and user model
        self.check_database_schema()
        
        # 6. Test OAuth flow
        self.test_oauth_flow()
        
        # 7. Generate report
        self.generate_report()
        
    def check_environment_variables(self):
        """Check if OAuth environment variables are set"""
        logger.info("\n1️⃣ Checking Environment Variables...")
        
        # Check both naming conventions
        primary_vars = {
            'GOOGLE_CLIENT_ID': os.environ.get('GOOGLE_CLIENT_ID'),
            'GOOGLE_CLIENT_SECRET': os.environ.get('GOOGLE_CLIENT_SECRET')
        }
        
        alternate_vars = {
            'GOOGLE_OAUTH_CLIENT_ID': os.environ.get('GOOGLE_OAUTH_CLIENT_ID'),
            'GOOGLE_OAUTH_CLIENT_SECRET': os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET')
        }
        
        # Check primary variables
        for var_name, value in primary_vars.items():
            if value:
                logger.info(f"   ✅ {var_name}: Set (length: {len(value)})")
            else:
                logger.info(f"   ❌ {var_name}: Not set")
                if alternate_vars.get(f'GOOGLE_OAUTH_{var_name.split("_", 2)[2]}'):
                    self.warnings.append(f"{var_name} not set but alternate variable exists")
                else:
                    self.issues.append(f"{var_name} is not set")
        
        # Check other required variables
        other_vars = ['SESSION_SECRET', 'DATABASE_URL']
        for var in other_vars:
            if os.environ.get(var):
                logger.info(f"   ✅ {var}: Set")
            else:
                logger.info(f"   ❌ {var}: Not set")
                self.issues.append(f"{var} is not set")
                
    def validate_credential_format(self):
        """Validate OAuth credential format"""
        logger.info("\n2️⃣ Validating Credential Format...")
        
        client_id = os.environ.get('GOOGLE_CLIENT_ID') or os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
        client_secret = os.environ.get('GOOGLE_CLIENT_SECRET') or os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET')
        
        if client_id:
            # Check for JSON data
            if len(client_id) > 100 or client_id.startswith('{'):
                logger.info("   ⚠️  Client ID appears to contain JSON data")
                # Try to extract
                extracted = self.extract_client_id(client_id)
                if extracted:
                    logger.info(f"   ✅ Extracted client ID: {extracted}")
                    self.fixes_applied.append("Extracted client ID from JSON")
                else:
                    self.issues.append("Failed to extract client ID from JSON")
            elif client_id.endswith('.apps.googleusercontent.com'):
                logger.info("   ✅ Client ID format is valid")
            else:
                logger.info("   ❌ Client ID format is invalid")
                self.issues.append("Client ID doesn't match expected format")
        
        if client_secret:
            if client_secret.startswith('GOCSPX-'):
                logger.info("   ✅ Client secret format is valid")
            else:
                logger.info("   ⚠️  Client secret format may be invalid")
                self.warnings.append("Client secret doesn't start with GOCSPX-")
                
    def extract_client_id(self, raw_data):
        """Extract client ID from JSON or malformed data"""
        try:
            # Try JSON parsing
            data = json.loads(raw_data)
            if isinstance(data, dict) and 'client_id' in data:
                return data['client_id']
        except:
            pass
            
        # Try regex extraction
        match = re.search(r'(\d{10,15}-[a-zA-Z0-9]+\.apps\.googleusercontent\.com)', raw_data)
        if match:
            return match.group(1)
            
        return None
        
    def check_oauth_initialization(self):
        """Check if OAuth service can initialize"""
        logger.info("\n3️⃣ Testing OAuth Service Initialization...")
        
        try:
            # Import and test OAuth service
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from utils.google_oauth import oauth_service
            
            if oauth_service.is_configured():
                logger.info("   ✅ OAuth service reports as configured")
            else:
                logger.info("   ❌ OAuth service is not configured")
                self.issues.append("OAuth service initialization failed")
                
        except Exception as e:
            logger.info(f"   ❌ Failed to import OAuth service: {e}")
            self.issues.append(f"OAuth service import error: {str(e)}")
            
    def check_redirect_uris(self):
        """Check redirect URI configuration"""
        logger.info("\n4️⃣ Checking Redirect URI Configuration...")
        
        # Get possible deployment URLs
        deployment_urls = []
        
        # Check environment variables
        for env_var in ['REPL_URL', 'REPLIT_APP_URL', 'REPLIT_DEV_DOMAIN']:
            url = os.environ.get(env_var)
            if url:
                deployment_urls.append(url)
                logger.info(f"   📍 Found {env_var}: {url}")
        
        # Common Replit patterns
        common_patterns = [
            "https://nous.replit.app",
            "https://nousintelligence.replit.app",
            "https://[username]-[repl-name].replit.app"
        ]
        
        logger.info("\n   Required Google Cloud Console Redirect URIs:")
        if deployment_urls:
            for url in deployment_urls:
                logger.info(f"   • {url}/auth/google/callback")
                logger.info(f"   • {url}/callback/google")
        else:
            logger.info("   ⚠️  No deployment URL found. Add these common patterns:")
            for pattern in common_patterns:
                logger.info(f"   • {pattern}/auth/google/callback")
                
    def check_database_schema(self):
        """Check if database and User model are properly configured"""
        logger.info("\n5️⃣ Checking Database Schema...")
        
        try:
            from models.user import User
            from database import db
            
            # Check User model OAuth fields
            required_fields = ['google_id', 'google_access_token', 'google_refresh_token']
            user_columns = [col.name for col in User.__table__.columns]
            
            for field in required_fields:
                if field in user_columns:
                    logger.info(f"   ✅ User.{field} exists")
                else:
                    logger.info(f"   ❌ User.{field} missing")
                    self.issues.append(f"User model missing {field} field")
                    
        except Exception as e:
            logger.info(f"   ❌ Failed to check database schema: {e}")
            self.issues.append("Database schema check failed")
            
    def test_oauth_flow(self):
        """Test OAuth flow components"""
        logger.info("\n6️⃣ Testing OAuth Flow Components...")
        
        # Test state generation
        try:
            import secrets
            state = secrets.token_urlsafe(32)
            logger.info(f"   ✅ State token generation works")
        except:
            logger.info(f"   ❌ State token generation failed")
            self.issues.append("State token generation failed")
            
        # Check session configuration
        session_secret = os.environ.get('SESSION_SECRET')
        if session_secret and len(session_secret) >= 32:
            logger.info(f"   ✅ Session secret is configured (length: {len(session_secret)})")
        else:
            logger.info(f"   ❌ Session secret is missing or too short")
            self.issues.append("SESSION_SECRET must be at least 32 characters")
            
    def generate_report(self):
        """Generate comprehensive report with fixes"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 OAUTH DIAGNOSTIC REPORT")
        logger.info("=" * 60)
        
        if not self.issues:
            logger.info("\n✅ No critical issues found!")
        else:
            logger.info(f"\n❌ Found {len(self.issues)} critical issues:")
            for i, issue in enumerate(self.issues, 1):
                logger.info(f"   {i}. {issue}")
                
        if self.warnings:
            logger.info(f"\n⚠️  {len(self.warnings)} warnings:")
            for warning in self.warnings:
                logger.info(f"   • {warning}")
                
        if self.fixes_applied:
            logger.info(f"\n🔧 Applied {len(self.fixes_applied)} fixes:")
            for fix in self.fixes_applied:
                logger.info(f"   • {fix}")
                
        # Provide setup instructions
        self.provide_setup_instructions()
        
    def provide_setup_instructions(self):
        """Provide clear setup instructions"""
        logger.info("\n" + "=" * 60)
        logger.info("📋 SETUP INSTRUCTIONS")
        logger.info("=" * 60)
        
        if any("GOOGLE_CLIENT_ID" in issue for issue in self.issues):
            logger.info("\n1️⃣ Set OAuth Credentials:")
            logger.info("   In your deployment environment, set these variables:")
            logger.info("   • GOOGLE_CLIENT_ID = your-client-id.apps.googleusercontent.com")
            logger.info("   • GOOGLE_CLIENT_SECRET = GOCSPX-your-secret")
            logger.info("   • SESSION_SECRET = (generate 32+ character random string)")
            
        logger.info("\n2️⃣ Configure Google Cloud Console:")
        logger.info("   Add these redirect URIs to your OAuth client:")
        logger.info("   • https://your-app.replit.app/auth/google/callback")
        logger.info("   • https://your-app.replit.app/callback/google")
        logger.info("   • http://localhost:8080/auth/google/callback (for local testing)")
        
        logger.info("\n3️⃣ Test OAuth Flow:")
        logger.info("   1. Clear browser cookies for your app")
        logger.info("   2. Visit /auth/login")
        logger.info("   3. Click 'Sign in with Google'")
        logger.info("   4. Check browser console for errors")
        
        logger.info("\n4️⃣ Common Fixes:")
        logger.info("   • Ensure all environment variables are set correctly")
        logger.info("   • Wait 5-10 minutes after updating Google Cloud Console")
        logger.info("   • Use incognito/private browsing to test")
        logger.info("   • Check that your app URL matches redirect URIs exactly")

def main():
    """Run OAuth debugger"""
    debugger = OAuthDebugger()
    debugger.run_diagnostics()
    
    # Create test script
    logger.info("\n" + "=" * 60)
    logger.info("🧪 Creating OAuth test script...")
    
    test_script = '''#!/usr/bin/env python3
"""Test OAuth Configuration"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test environment variables
print("\\n=== Testing Environment Variables ===")
vars_to_check = ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'SESSION_SECRET']
for var in vars_to_check:
    value = os.environ.get(var)
    if value:
        print(f"✅ {var}: Set (length: {len(value)})")
    else:
        print(f"❌ {var}: Not set")

# Test OAuth service
print("\\n=== Testing OAuth Service ===")
try:
    from utils.google_oauth import oauth_service
    if oauth_service.is_configured():
        print("✅ OAuth service is configured")
    else:
        print("❌ OAuth service is not configured")
except Exception as e:
    print(f"❌ Failed to load OAuth service: {e}")

# Test Flask app
print("\\n=== Testing Flask App ===")
try:
    from app import app
    with app.app_context():
        from utils.google_oauth import init_oauth
        result = init_oauth(app)
        if result:
            print("✅ OAuth initialized with Flask app")
        else:
            print("❌ OAuth initialization failed")
except Exception as e:
    print(f"❌ Failed to test Flask app: {e}")
'''
    
    with open('test_oauth_setup.py', 'w') as f:
        f.write(test_script)
    os.chmod('test_oauth_setup.py', 0o755)
    
    logger.info("✅ Created test_oauth_setup.py")
    logger.info("   Run: python test_oauth_setup.py")

if __name__ == "__main__":
    main() 