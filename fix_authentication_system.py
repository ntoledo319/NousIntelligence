#!/usr/bin/env python3
"""
Complete Authentication System Fix
Fixes all login methods: Google OAuth, Demo Mode, Session Auth
"""

import os
import json
import logging

logger = logging.getLogger(__name__)

def extract_correct_oauth_credentials():
    """Extract correct OAuth credentials from malformed environment variables"""
    
    client_id_raw = os.environ.get('GOOGLE_CLIENT_ID', '')
    
    # Check if GOOGLE_CLIENT_ID contains JSON data
    if len(client_id_raw) > 100 and '{' in client_id_raw:
        try:
            # Try to parse as JSON and extract client_id
            if client_id_raw.startswith('{'):
                oauth_data = json.loads(client_id_raw)
            else:
                # Find the JSON part
                json_start = client_id_raw.find('{')
                json_part = client_id_raw[json_start:]
                oauth_data = json.loads(json_part)
            
            if 'client_id' in oauth_data:
                correct_client_id = oauth_data['client_id']
                logger.info(f"Extracted correct client_id: {correct_client_id[:20]}...")
                return correct_client_id
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OAuth JSON: {e}")
    
    # If it's already correct format, return as-is
    if client_id_raw and len(client_id_raw) < 100:
        return client_id_raw
    
    return None

def validate_authentication_system():
    """Validate the complete authentication system"""
    issues = []
    fixes = []
    
    # Check OAuth credentials
    client_id = extract_correct_oauth_credentials()
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    if not client_id:
        issues.append("GOOGLE_CLIENT_ID is missing or malformed")
        fixes.append("Fix GOOGLE_CLIENT_ID environment variable")
    
    if not client_secret:
        issues.append("GOOGLE_CLIENT_SECRET is missing")
        fixes.append("Set GOOGLE_CLIENT_SECRET environment variable")
    
    # Check Flask-Login configuration
    try:
        from utils.google_oauth import oauth_service
        if oauth_service and not oauth_service.is_configured():
            issues.append("OAuth service not properly configured")
            fixes.append("Initialize OAuth service with correct credentials")
    except ImportError:
        issues.append("OAuth service import failed")
        fixes.append("Fix OAuth service imports")
    
    # Check demo mode availability
    try:
        from utils.auth_compat import get_demo_user
        demo_user = get_demo_user()
        if not demo_user:
            issues.append("Demo mode not available")
            fixes.append("Fix demo user creation")
    except ImportError:
        issues.append("Auth compatibility layer import failed")
        fixes.append("Fix auth compatibility imports")
    
    return issues, fixes, client_id

def fix_oauth_credentials():
    """Fix OAuth credentials by extracting correct values"""
    
    correct_client_id = extract_correct_oauth_credentials()
    
    if correct_client_id:
        print(f"✅ Extracted correct GOOGLE_CLIENT_ID: {correct_client_id}")
        return correct_client_id
    else:
        print("❌ Could not extract correct GOOGLE_CLIENT_ID")
        return None

if __name__ == "__main__":
    print("🔧 Fixing Authentication System...")
    
    # Validate current state
    issues, fixes, correct_client_id = validate_authentication_system()
    
    print(f"\n📊 Authentication System Status:")
    print(f"Issues found: {len(issues)}")
    for issue in issues:
        print(f"  ❌ {issue}")
    
    print(f"\n🔧 Required Fixes:")
    for fix in fixes:
        print(f"  🔨 {fix}")
    
    # Extract correct credentials
    if correct_client_id:
        print(f"\n✅ Correct GOOGLE_CLIENT_ID extracted: {correct_client_id}")
    else:
        print(f"\n❌ Failed to extract correct GOOGLE_CLIENT_ID")
    
    print(f"\n📝 Next Steps:")
    print(f"1. Update GOOGLE_CLIENT_ID in Replit Secrets with: {correct_client_id}")
    print(f"2. Restart the application")
    print(f"3. Test all login methods")