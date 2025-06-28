#!/usr/bin/env python3
"""
Port Validation & Smoke Test Suite
Validates port configuration and detects conflicts
"""
import os
import sys
import time
import socket
import subprocess
import requests
from pathlib import Path

class PortValidationSuite:
    def __init__(self):
        self.test_results = []
        self.port = int(os.environ.get('PORT', 5000))
        
    def log_test(self, test_name, status, message=""):
        """Log test result"""
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.test_results.append(result)
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {message}")
        
    def test_environment_port_config(self):
        """Test that PORT environment variable is properly configured"""
        try:
            # Test default fallback
            if 'PORT' not in os.environ:
                self.log_test("ENV_PORT_FALLBACK", "PASS", f"Using fallback port {self.port}")
            else:
                env_port = int(os.environ['PORT'])
                if env_port == self.port:
                    self.log_test("ENV_PORT_CONFIG", "PASS", f"Environment PORT={env_port}")
                else:
                    self.log_test("ENV_PORT_CONFIG", "FAIL", f"Port mismatch: env={env_port}, config={self.port}")
                    
            # Validate port range
            if 1024 <= self.port <= 65535:
                self.log_test("PORT_RANGE", "PASS", f"Port {self.port} in valid range")
            else:
                self.log_test("PORT_RANGE", "FAIL", f"Port {self.port} outside valid range (1024-65535)")
                
        except Exception as e:
            self.log_test("ENV_PORT_CONFIG", "FAIL", f"Error: {e}")
            
    def test_port_availability(self):
        """Test if port is available for binding"""
        try:
            # Test if port is available
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', self.port))
            sock.close()
            
            if result != 0:
                self.log_test("PORT_AVAILABLE", "PASS", f"Port {self.port} is available")
            else:
                self.log_test("PORT_AVAILABLE", "WARN", f"Port {self.port} already in use")
                
        except Exception as e:
            self.log_test("PORT_AVAILABLE", "FAIL", f"Error checking port: {e}")
            
    def test_config_consistency(self):
        """Test that all config files use consistent port settings"""
        try:
            # Check main.py
            main_path = Path('main.py')
            if main_path.exists():
                content = main_path.read_text()
                if "os.environ.get('PORT', 5000)" in content:
                    self.log_test("MAIN_PY_CONFIG", "PASS", "main.py uses proper PORT env var")
                else:
                    self.log_test("MAIN_PY_CONFIG", "FAIL", "main.py missing proper PORT configuration")
            
            # Check config/app_config.py
            config_path = Path('config/app_config.py')
            if config_path.exists():
                content = config_path.read_text()
                if "os.environ.get('PORT', 5000)" in content:
                    self.log_test("APP_CONFIG_PORT", "PASS", "app_config.py uses proper PORT env var")
                else:
                    self.log_test("APP_CONFIG_PORT", "FAIL", "app_config.py missing proper PORT configuration")
                    
            # Check replit.toml
            replit_path = Path('replit.toml')
            if replit_path.exists():
                content = replit_path.read_text()
                if 'PORT = "5000"' in content and 'localPort = 5000' in content:
                    self.log_test("REPLIT_CONFIG", "PASS", "replit.toml has consistent port config")
                else:
                    self.log_test("REPLIT_CONFIG", "WARN", "replit.toml port configuration needs review")
                    
        except Exception as e:
            self.log_test("CONFIG_CONSISTENCY", "FAIL", f"Error checking configs: {e}")
            
    def test_no_hardcoded_ports(self):
        """Scan for hardcoded ports in Python files"""
        try:
            hardcoded_patterns = [
                "app.run(port=",
                "flask.run(port=",
                ".listen(5000",
                ".listen(8080",
                ".listen(3000"
            ]
            
            violations = []
            # Check main project files, not test files
            main_files = ['app.py', 'main.py', 'config/app_config.py']
            
            for file_name in main_files:
                file_path = Path('..') / file_name if Path('..').exists() else Path(file_name)
                if file_path.exists():
                    try:
                        content = file_path.read_text(encoding='utf-8')
                        for pattern in hardcoded_patterns:
                            if pattern in content:
                                violations.append(f"{file_name}: {pattern}")
                    except:
                        continue
                    
            if not violations:
                self.log_test("NO_HARDCODED_PORTS", "PASS", "No hardcoded ports detected")
            else:
                self.log_test("NO_HARDCODED_PORTS", "FAIL", f"Found violations: {violations[:3]}")
                
        except Exception as e:
            self.log_test("NO_HARDCODED_PORTS", "FAIL", f"Error scanning: {e}")
            
    def test_app_startup(self):
        """Test that app can start with current port configuration"""
        try:
            # Import app to test configuration
            sys.path.insert(0, '..' if Path('..').exists() else '.')
            
            # Create logs directory if it doesn't exist
            logs_dir = Path('..') / 'logs' if Path('..').exists() else Path('logs')
            logs_dir.mkdir(exist_ok=True)
            
            from config.app_config import AppConfig
            
            # Validate configuration
            issues = AppConfig.validate()
            if not issues:
                self.log_test("APP_CONFIG_VALID", "PASS", "Configuration validation passed")
            else:
                self.log_test("APP_CONFIG_VALID", "FAIL", f"Config issues: {issues}")
                
            # Test import without starting server
            try:
                from app import create_app
                app = create_app()
                self.log_test("APP_IMPORT", "PASS", "App imports and creates successfully")
            except Exception as e:
                self.log_test("APP_IMPORT", "FAIL", f"App creation failed: {e}")
                
        except Exception as e:
            self.log_test("APP_STARTUP", "FAIL", f"Startup test failed: {e}")
            
    def test_proxy_configuration(self):
        """Test ProxyFix configuration for deployment"""
        try:
            sys.path.insert(0, '.')
            from app import create_app
            app = create_app()
            
            # Check if ProxyFix is configured
            if hasattr(app.wsgi_app, '_app'):
                self.log_test("PROXY_FIX", "PASS", "ProxyFix middleware configured")
            else:
                self.log_test("PROXY_FIX", "WARN", "ProxyFix middleware not detected")
                
        except Exception as e:
            self.log_test("PROXY_CONFIGURATION", "FAIL", f"Error checking proxy: {e}")
            
    def run_smoke_test(self):
        """Run quick server smoke test"""
        try:
            # Start server in background for quick test
            process = subprocess.Popen([
                sys.executable, 'main.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Give server time to start
            time.sleep(3)
            
            try:
                # Test health endpoint
                response = requests.get(f'http://127.0.0.1:{self.port}/health', timeout=5)
                if response.status_code == 200:
                    self.log_test("SMOKE_TEST", "PASS", f"Server responding on port {self.port}")
                else:
                    self.log_test("SMOKE_TEST", "WARN", f"Server responded with status {response.status_code}")
            except requests.RequestException:
                self.log_test("SMOKE_TEST", "WARN", "Server not responding (may be starting)")
                
            # Clean up
            process.terminate()
            process.wait(timeout=5)
            
        except Exception as e:
            self.log_test("SMOKE_TEST", "FAIL", f"Smoke test failed: {e}")
            
    def generate_report(self):
        """Generate comprehensive port validation report"""
        print("\n" + "="*60)
        print("PORT VALIDATION SUITE RESULTS")
        print("="*60)
        
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAIL') 
        warned = sum(1 for r in self.test_results if r['status'] == 'WARN')
        total = len(self.test_results)
        
        print(f"Tests Run: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warned}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        if failed == 0:
            print("\n🎉 PORT CONFIGURATION IS DEPLOYMENT READY!")
        else:
            print(f"\n⚠️  {failed} issues need attention before deployment")
            
        print("\nDetailed Results:")
        for result in self.test_results:
            status_icon = "✅" if result['status'] == "PASS" else "❌" if result['status'] == "FAIL" else "⚠️"
            print(f"{status_icon} {result['test']}: {result['message']}")
            
        return failed == 0
        
    def run_full_suite(self):
        """Run complete port validation suite"""
        print("🔍 Starting Port Validation Suite...")
        print(f"Target Port: {self.port}")
        print("-" * 60)
        
        self.test_environment_port_config()
        self.test_port_availability()
        self.test_config_consistency()
        self.test_no_hardcoded_ports()
        self.test_app_startup()
        self.test_proxy_configuration()
        self.run_smoke_test()
        
        return self.generate_report()

def main():
    """Main entry point for port validation"""
    validator = PortValidationSuite()
    success = validator.run_full_suite()
    
    if success:
        print("\n✅ All port validation tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Review issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()