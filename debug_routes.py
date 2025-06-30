#!/usr/bin/env python3
"""Debug route registration issues"""

import sys
from app_working import app

def debug_routes():
    """Debug route registration"""
    print("🔍 Debugging NOUS Route Registration")
    print("=" * 50)
    
    with app.app_context():
        print(f"📊 Total registered blueprints: {len(app.blueprints)}")
        
        for name, blueprint in app.blueprints.items():
            print(f"✅ Blueprint: {name}")
        
        print("\n🛣️  All registered routes:")
        for rule in app.url_map.iter_rules():
            print(f"  {rule.rule} → {rule.endpoint} ({rule.methods})")
        
        print("\n🔍 Looking for index/demo routes:")
        demo_routes = [rule for rule in app.url_map.iter_rules() if 'demo' in rule.rule]
        if demo_routes:
            for route in demo_routes:
                print(f"  ✅ {route.rule} → {route.endpoint}")
        else:
            print("  ❌ No demo routes found")
        
        print("\n🔍 Checking index blueprint specifically:")
        if 'index' in app.blueprints:
            print("  ✅ Index blueprint is registered")
        else:
            print("  ❌ Index blueprint not registered")

if __name__ == "__main__":
    debug_routes()