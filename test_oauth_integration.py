#!/usr/bin/env python3
"""
Test script for OAuth integration validation
Runs independently to avoid circular import issues
"""

import os
import json
import requests
from datetime import datetime

def test_google_oauth_credentials():
    """Test Google OAuth credential loading and validation"""
    print("Testing Google OAuth Integration...")
    
    # Test client_secret.json loading
    try:
        with open('client_secret.json', 'r') as f:
            client_info = json.load(f)
            
        if 'web' in client_info:
            web_info = client_info['web']
            client_id = web_info.get('client_id')
            client_secret = web_info.get('client_secret')
            
            print(f"✅ Client credentials loaded from file")
            print(f"   Client ID: {client_id[:20]}...")
            print(f"   Redirect URIs: {len(web_info.get('redirect_uris', []))} configured")
            
            # Test OAuth discovery endpoint
            try:
                discovery_url = 'https://accounts.google.com/.well-known/openid-configuration'
                response = requests.get(discovery_url, timeout=10)
                response.raise_for_status()
                
                discovery_data = response.json()
                print(f"✅ Google OAuth discovery endpoint accessible")
                print(f"   Authorization endpoint: {discovery_data.get('authorization_endpoint')}")
                print(f"   Token endpoint: {discovery_data.get('token_endpoint')}")
                
                return True
            except Exception as e:
                print(f"❌ Google OAuth discovery failed: {e}")
                return False
        else:
            print("❌ Invalid client_secret.json format")
            return False
    except Exception as e:
        print(f"❌ Error loading client_secret.json: {e}")
        return False

def test_ai_services():
    """Test AI service integrations"""
    print("\nTesting AI Services...")
    
    services = {
        'OpenAI': {
            'key': os.environ.get('OPENAI_API_KEY'),
            'url': 'https://api.openai.com/v1/models'
        },
        'OpenRouter': {
            'key': os.environ.get('OPENROUTER_API_KEY'),
            'url': 'https://openrouter.ai/api/v1/models'
        },
        'Hugging Face': {
            'key': os.environ.get('HUGGINGFACE_API_KEY'),
            'url': 'https://huggingface.co/api/whoami-v2'
        }
    }
    
    results = {}
    
    for service_name, config in services.items():
        if not config['key']:
            print(f"⚠️  {service_name}: No API key configured")
            results[service_name] = 'not_configured'
            continue
            
        try:
            headers = {
                'Authorization': f'Bearer {config["key"]}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(config['url'], headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {service_name}: API key valid and service accessible")
                results[service_name] = 'healthy'
            else:
                print(f"❌ {service_name}: API returned status {response.status_code}")
                results[service_name] = 'error'
                
        except Exception as e:
            print(f"❌ {service_name}: Connection failed - {e}")
            results[service_name] = 'error'
    
    return results

def test_database_config():
    """Test database configuration"""
    print("\nTesting Database Configuration...")
    
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not configured")
        return False
        
    if database_url.startswith('postgresql://'):
        print("✅ PostgreSQL database configured")
        print(f"   Connection string format: Valid")
        return True
    elif database_url.startswith('sqlite:///'):
        print("✅ SQLite database configured")
        print(f"   Database file: {database_url.replace('sqlite:///', '')}")
        return True
    else:
        print(f"❌ Unknown database type: {database_url.split('://')[0]}")
        return False

def generate_audit_summary():
    """Generate final audit summary"""
    print("\n" + "="*60)
    print("API & OAUTH RELIABILITY AUDIT SUMMARY")
    print("="*60)
    
    # Test all services
    google_oauth = test_google_oauth_credentials()
    ai_services = test_ai_services()
    database = test_database_config()
    
    # Count results
    healthy_count = sum(1 for status in ai_services.values() if status == 'healthy')
    error_count = sum(1 for status in ai_services.values() if status == 'error')
    not_configured_count = sum(1 for status in ai_services.values() if status == 'not_configured')
    
    # Add Google OAuth and database to counts
    if google_oauth:
        healthy_count += 1
    else:
        error_count += 1
        
    if database:
        healthy_count += 1
    else:
        error_count += 1
    
    # Determine overall status
    if error_count == 0:
        overall_status = "HEALTHY"
    elif healthy_count > 0:
        overall_status = "DEGRADED"
    else:
        overall_status = "UNHEALTHY"
    
    print(f"\nOverall Status: {overall_status}")
    print(f"Services: {healthy_count} healthy, {error_count} errors, {not_configured_count} not configured")
    
    print(f"\nTimestamp: {datetime.utcnow().isoformat()}Z")
    print("="*60)
    
    return {
        'overall_status': overall_status,
        'healthy': healthy_count,
        'errors': error_count,
        'not_configured': not_configured_count,
        'google_oauth': google_oauth,
        'ai_services': ai_services,
        'database': database
    }

if __name__ == '__main__':
    results = generate_audit_summary()
    
    # Exit with appropriate code
    if results['overall_status'] == 'HEALTHY':
        exit(0)
    elif results['overall_status'] == 'DEGRADED':
        exit(1)
    else:
        exit(2)