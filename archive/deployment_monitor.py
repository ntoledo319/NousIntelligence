#!/usr/bin/env python3
"""
Deployment Success Monitor
Real-time monitoring to ensure 100% deployment success
"""
import os
import sys
import time
import json
import requests
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import logging

class DeploymentMonitor:
    def __init__(self):
        self.start_time = datetime.now()
        self.checks_passed = 0
        self.checks_failed = 0
        self.deployment_url = None
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(levelname)s: %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def log_success(self, message):
        """Log a successful check"""
        self.checks_passed += 1
        self.logger.info(f"✅ {message}")
        print(f"✅ {message}")
    
    def log_failure(self, message):
        """Log a failed check"""
        self.checks_failed += 1
        self.logger.error(f"❌ {message}")
        print(f"❌ {message}")
    
    def log_info(self, message):
        """Log informational message"""
        self.logger.info(f"ℹ️  {message}")
        print(f"ℹ️  {message}")
    
    def check_environment_setup(self):
        """Check if environment is properly configured"""
        self.log_info("Checking environment setup...")
        
        # Check for required files
        required_files = ['main.py', 'app.py', 'replit.toml', 'pyproject.toml']
        for file in required_files:
            if Path(file).exists():
                self.log_success(f"Required file exists: {file}")
            else:
                self.log_failure(f"Missing required file: {file}")
                return False
        
        # Check replit.toml configuration
        try:
            with open('replit.toml', 'r') as f:
                content = f.read()
                if 'python3' in content and 'main.py' in content:
                    self.log_success("replit.toml properly configured")
                else:
                    self.log_failure("replit.toml missing key configurations")
                    return False
        except Exception as e:
            self.log_failure(f"Error reading replit.toml: {e}")
            return False
        
        return True
    
    def check_app_startup(self):
        """Check if app can start successfully"""
        self.log_info("Testing app startup...")
        
        try:
            # Test import
            sys.path.insert(0, '.')
            from app import create_app
            
            # Create app
            app = create_app()
            self.log_success("App creation successful")
            
            # Test app context
            with app.app_context():
                self.log_success("App context works")
            
            return True
            
        except Exception as e:
            self.log_failure(f"App startup failed: {e}")
            return False
    
    def check_health_endpoints(self):
        """Check if health endpoints are accessible"""
        self.log_info("Checking health endpoints...")
        
        # Start the app in background
        try:
            proc = subprocess.Popen([
                sys.executable, 'main.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for app to start
            time.sleep(3)
            
            # Test health endpoint
            try:
                response = requests.get('http://localhost:5000/health', timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'healthy':
                        self.log_success("Health endpoint working correctly")
                        health_ok = True
                    else:
                        self.log_failure(f"Health endpoint returned unhealthy status: {data}")
                        health_ok = False
                else:
                    self.log_failure(f"Health endpoint returned status {response.status_code}")
                    health_ok = False
                    
            except Exception as e:
                self.log_failure(f"Health endpoint test failed: {e}")
                health_ok = False
            
            # Test readiness endpoint
            try:
                response = requests.get('http://localhost:5000/ready', timeout=5)
                if response.status_code == 200:
                    self.log_success("Readiness endpoint working")
                    ready_ok = True
                else:
                    self.log_failure(f"Readiness endpoint returned status {response.status_code}")
                    ready_ok = False
            except Exception as e:
                self.log_failure(f"Readiness endpoint test failed: {e}")
                ready_ok = False
            
            # Clean up
            proc.terminate()
            proc.wait(timeout=5)
            
            return health_ok and ready_ok
            
        except Exception as e:
            self.log_failure(f"Failed to start app for endpoint testing: {e}")
            return False
    
    def check_deployment_readiness(self):
        """Comprehensive deployment readiness check"""
        self.log_info("Running comprehensive deployment readiness check...")
        
        checks = [
            ("Environment Setup", self.check_environment_setup),
            ("App Startup", self.check_app_startup),
            ("Health Endpoints", self.check_health_endpoints)
        ]
        
        all_passed = True
        
        for check_name, check_func in checks:
            self.log_info(f"Running {check_name} check...")
            try:
                if check_func():
                    self.log_success(f"{check_name} check PASSED")
                else:
                    self.log_failure(f"{check_name} check FAILED")
                    all_passed = False
            except Exception as e:
                self.log_failure(f"{check_name} check ERROR: {e}")
                all_passed = False
            
            print()  # Add spacing between checks
        
        return all_passed
    
    def generate_deployment_report(self):
        """Generate a comprehensive deployment report"""
        duration = datetime.now() - self.start_time
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": duration.total_seconds(),
            "checks_passed": self.checks_passed,
            "checks_failed": self.checks_failed,
            "success_rate": (self.checks_passed / (self.checks_passed + self.checks_failed)) * 100 if (self.checks_passed + self.checks_failed) > 0 else 0,
            "deployment_ready": self.checks_failed == 0,
            "recommendations": []
        }
        
        if self.checks_failed > 0:
            report["recommendations"].append("Fix failed checks before deploying")
        else:
            report["recommendations"].append("Ready for production deployment")
        
        # Save report
        report_path = Path('deployment_readiness_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def print_summary(self, report):
        """Print deployment summary"""
        print("\n" + "=" * 60)
        print("🚀 DEPLOYMENT READINESS SUMMARY")
        print("=" * 60)
        
        print(f"✅ Checks Passed: {report['checks_passed']}")
        print(f"❌ Checks Failed: {report['checks_failed']}")
        print(f"📊 Success Rate: {report['success_rate']:.1f}%")
        print(f"⏱️  Duration: {report['duration_seconds']:.1f}s")
        
        if report['deployment_ready']:
            print("\n🎉 DEPLOYMENT STATUS: ✅ READY FOR PRODUCTION!")
            print("📋 Next Steps:")
            print("  1. Click 'Deploy' in Replit")
            print("  2. Monitor health endpoints after deployment")
            print("  3. Verify application functionality")
        else:
            print("\n⚠️  DEPLOYMENT STATUS: ❌ NOT READY")
            print("📋 Required Actions:")
            for rec in report['recommendations']:
                print(f"  • {rec}")
        
        print("\n📄 Full report saved to: deployment_readiness_report.json")
        print("=" * 60)
    
    def run(self):
        """Run the complete deployment monitoring suite"""
        print("🚀 DEPLOYMENT SUCCESS MONITOR")
        print("=" * 60)
        print("Ensuring 100% deployment success...")
        print()
        
        # Run all checks
        deployment_ready = self.check_deployment_readiness()
        
        # Generate and display report
        report = self.generate_deployment_report()
        self.print_summary(report)
        
        return deployment_ready

def main():
    """Main entry point"""
    monitor = DeploymentMonitor()
    success = monitor.run()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())