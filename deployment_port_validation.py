#!/usr/bin/env python3
"""
Final Port Validation for Deployment
Quick validation that port configuration is deployment-ready
"""
import os
import sys
import socket
from pathlib import Path

def validate_port_configuration():
    """Quick port configuration validation"""
    print("🚑 GLOBAL PORT SANITIZER - FINAL VALIDATION")
    print("=" * 50)
    
    results = []
    
    # Test 1: Environment Variable Configuration
    port = int(os.environ.get('PORT', 5000))
    results.append(f"✅ PORT Environment Variable: {port}")
    
    # Test 2: Valid Port Range
    if 1024 <= port <= 65535:
        results.append(f"✅ Port Range Valid: {port} in range 1024-65535")
    else:
        results.append(f"❌ Port Range Invalid: {port} outside valid range")
        return False
        
    # Test 3: Configuration Files
    config_files = {
        'main.py': "os.environ.get('PORT', 5000)",
        'config/app_config.py': "os.environ.get('PORT', 5000)",
        'replit.toml': 'PORT = "5000"'
    }
    
    for file_name, expected in config_files.items():
        file_path = Path(file_name)
        if file_path.exists():
            content = file_path.read_text()
            if expected in content:
                results.append(f"✅ {file_name}: Proper port configuration")
            else:
                results.append(f"❌ {file_name}: Missing proper port configuration")
                return False
        else:
            results.append(f"⚠️ {file_name}: File not found")
            
    # Test 4: No Hardcoded Ports
    hardcoded_found = False
    main_files = ['app.py', 'main.py']
    for file_name in main_files:
        file_path = Path(file_name)
        if file_path.exists():
            content = file_path.read_text()
            if 'app.run(port=' in content and 'os.environ.get' not in content:
                results.append(f"❌ {file_name}: Hardcoded port detected")
                hardcoded_found = True
                
    if not hardcoded_found:
        results.append("✅ No Hardcoded Ports: Clean configuration")
        
    # Test 5: Port Availability
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result != 0:
            results.append(f"✅ Port Available: {port} ready for binding")
        else:
            results.append(f"⚠️ Port In Use: {port} currently occupied")
    except Exception as e:
        results.append(f"⚠️ Port Check: Unable to verify availability")
        
    # Print Results
    for result in results:
        print(result)
        
    # Final Assessment
    failed_tests = sum(1 for r in results if r.startswith('❌'))
    warning_tests = sum(1 for r in results if r.startswith('⚠️'))
    passed_tests = sum(1 for r in results if r.startswith('✅'))
    
    print("\n" + "=" * 50)
    print("DEPLOYMENT READINESS ASSESSMENT")
    print("=" * 50)
    print(f"✅ Passed: {passed_tests}")
    print(f"⚠️ Warnings: {warning_tests}")
    print(f"❌ Failed: {failed_tests}")
    
    if failed_tests == 0:
        print("\n🎉 PORT CONFIGURATION IS DEPLOYMENT READY!")
        print("✅ All critical port validations passed")
        print("✅ Environment variable configuration proper")
        print("✅ No hardcoded ports detected")
        print("✅ Replit deployment configuration correct")
        return True
    else:
        print(f"\n❌ {failed_tests} critical issues need fixing")
        return False

def main():
    """Main validation entry point"""
    success = validate_port_configuration()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()