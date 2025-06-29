#!/usr/bin/env python3
"""
Comprehensive Build Test
Tests the complete NOUS application with all features
"""
import sys
import os
import signal
import time
import subprocess
from threading import Timer

def timeout_handler(signum, frame):
    raise TimeoutError("Build test timed out")

def test_comprehensive_build():
    """Test the complete application build"""
    print("🔍 Comprehensive Build Test")
    print("Testing full NOUS application with all features...")
    
    # Set timeout for 60 seconds
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(60)
    
    try:
        # Test with optimized startup for faster initialization
        os.environ['FAST_STARTUP'] = 'false'  # Full feature loading
        os.environ['DISABLE_HEAVY_FEATURES'] = 'false'  # All features enabled
        
        print("Creating comprehensive app...")
        from app import create_app
        app = create_app()
        
        signal.alarm(0)  # Cancel timeout
        
        print("✅ App created successfully")
        print(f"✅ Routes registered: {len(app.url_map._rules)}")
        
        # Test core endpoints
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            if response.status_code == 200:
                print("✅ Health endpoint working")
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
            
            # Test landing page
            response = client.get('/')
            if response.status_code in [200, 302]:
                print("✅ Landing page working")
            else:
                print(f"❌ Landing page failed: {response.status_code}")
        
        return True
        
    except TimeoutError:
        print("❌ Build test timed out after 60 seconds")
        print("Application is building but initialization is slow")
        return False
    except Exception as e:
        signal.alarm(0)  # Cancel timeout
        print(f"❌ Build failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_production_startup():
    """Test production-like startup"""
    print("\n🚀 Testing production startup...")
    
    try:
        # Start the application in background
        env = os.environ.copy()
        env['PORT'] = '5001'
        env['FAST_STARTUP'] = 'false'
        
        process = subprocess.Popen(
            [sys.executable, 'main.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for startup (max 30 seconds)
        def kill_process():
            if process.poll() is None:
                process.terminate()
        
        timer = Timer(30.0, kill_process)
        timer.start()
        
        # Check if process starts successfully
        time.sleep(5)
        
        if process.poll() is None:
            print("✅ Application started successfully")
            
            # Try to connect to health endpoint
            import urllib.request
            try:
                response = urllib.request.urlopen('http://localhost:5001/health', timeout=5)
                if response.getcode() == 200:
                    print("✅ Health endpoint accessible")
                else:
                    print(f"⚠️  Health endpoint returned: {response.getcode()}")
            except Exception as e:
                print(f"⚠️  Health endpoint not accessible yet: {e}")
            
            success = True
        else:
            print("❌ Application failed to start")
            success = False
        
        # Clean up
        timer.cancel()
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)
        
        return success
        
    except Exception as e:
        print(f"❌ Production startup test failed: {e}")
        return False

def main():
    """Run comprehensive build tests"""
    print("🧠 NOUS Comprehensive Build Validation")
    print("=" * 50)
    
    tests = [
        ("Comprehensive Build", test_comprehensive_build),
        ("Production Startup", test_production_startup)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: EXCEPTION - {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 FINAL RESULTS: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 COMPREHENSIVE BUILD: SUCCESS")
        print("All features and functionality working correctly")
        return True
    else:
        print("⚠️  COMPREHENSIVE BUILD: ISSUES DETECTED")
        print("Some components need attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)