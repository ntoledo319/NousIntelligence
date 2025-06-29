#!/usr/bin/env python3
"""
Debug script to examine Flask app routes and identify landing page issues
"""
import os
import sys
from app import create_app

def debug_flask_app():
    """Debug the Flask app routes and configuration"""
    print("🔍 FLASK APP DEBUG ANALYSIS")
    print("=" * 50)
    
    try:
        # Create the app
        app = create_app()
        print("✅ App created successfully")
        
        # Print configuration
        print(f"\n📋 App Configuration:")
        print(f"  - Debug: {app.debug}")
        print(f"  - Testing: {app.testing}")
        print(f"  - Secret Key: {'Set' if app.secret_key else 'Not Set'}")
        
        if app.config.get('SERVER_NAME'):
            print(f"  - Server Name: {app.config['SERVER_NAME']}")
        else:
            print("  - Server Name: Not configured")
            
        # List all routes
        print(f"\n🛣️  Registered Routes:")
        route_count = 0
        for rule in app.url_map.iter_rules():
            print(f"  - {rule.endpoint}: {rule.rule} ({', '.join(rule.methods)})")
            route_count += 1
        
        print(f"\nTotal routes registered: {route_count}")
        
        # Test the landing page route specifically
        print(f"\n🏠 Testing Landing Page Route:")
        with app.test_client() as client:
            try:
                response = client.get('/')
                print(f"  - Status Code: {response.status_code}")
                print(f"  - Content Type: {response.content_type}")
                print(f"  - Content Length: {len(response.data)} bytes")
                
                if response.status_code == 200:
                    print("  ✅ Landing page route works!")
                    # Check if it contains expected content
                    content = response.data.decode()
                    if 'NOUS' in content:
                        print("  ✅ Landing page contains NOUS branding")
                    if 'Try Demo Now' in content:
                        print("  ✅ Landing page contains demo button")
                else:
                    print(f"  ❌ Landing page failed with status {response.status_code}")
                    print(f"  Response: {response.data.decode()[:200]}")
                    
            except Exception as e:
                print(f"  ❌ Error testing landing page: {e}")
        
        # Test other key routes
        print(f"\n🧪 Testing Other Key Routes:")
        test_routes = ['/demo', '/health', '/api/user']
        
        with app.test_client() as client:
            for route in test_routes:
                try:
                    response = client.get(route)
                    status = "✅" if response.status_code < 400 else "❌"
                    print(f"  {status} {route}: {response.status_code}")
                except Exception as e:
                    print(f"  ❌ {route}: Error - {e}")
        
    except Exception as e:
        print(f"❌ Failed to create app: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_flask_app()