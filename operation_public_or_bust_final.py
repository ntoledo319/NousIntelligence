#!/usr/bin/env python3
"""
OPERATION PUBLIC-OR-BUST Final Deployment Validator
Completes the operation plan and generates deployment report
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path


class PublicDeploymentValidator:
    def __init__(self):
        self.fixes_applied = []
        self.warnings = []
        self.errors = []
        self.secrets_needed = []
        
    def log_fix(self, description):
        """Log a fix that was applied"""
        self.fixes_applied.append(description)
        print(f"✅ FIX: {description}")
        
    def log_warning(self, description):
        """Log a warning"""
        self.warnings.append(description)
        print(f"⚠️  WARNING: {description}")
        
    def log_error(self, description):
        """Log an error"""
        self.errors.append(description)
        print(f"❌ ERROR: {description}")
        
    def check_proxy_configuration(self):
        """Verify ProxyFix is properly configured"""
        print("\n🔍 Checking proxy configuration...")
        
        try:
            with open('app.py', 'r') as f:
                content = f.read()
                
            if 'ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)' in content:
                self.log_fix("ProxyFix properly configured for Replit")
            else:
                self.log_error("ProxyFix not found or misconfigured")
                
        except Exception as e:
            self.log_error(f"Could not check proxy configuration: {e}")
    
    def check_session_security(self):
        """Verify session security settings"""
        print("\n🔍 Checking session security...")
        
        try:
            with open('app.py', 'r') as f:
                content = f.read()
                
            security_checks = [
                ('SESSION_COOKIE_HTTPONLY=True', 'HTTPOnly cookies enabled'),
                ("SESSION_COOKIE_SAMESITE='Lax'", 'SameSite policy configured'),
                ('SESSION_COOKIE_SECURE=False', 'Secure flag correctly disabled for Replit HTTP')
            ]
            
            for check, description in security_checks:
                if check in content:
                    self.log_fix(description)
                else:
                    self.log_warning(f"Missing or misconfigured: {description}")
                    
        except Exception as e:
            self.log_error(f"Could not check session security: {e}")
    
    def check_auth_configuration(self):
        """Verify replit.toml auth settings"""
        print("\n🔍 Checking auth configuration...")
        
        try:
            with open('replit.toml', 'r') as f:
                content = f.read()
                
            if 'pageEnabled = false' in content and 'buttonEnabled = false' in content:
                self.log_fix("Replit auth properly disabled for public access")
            else:
                self.log_error("Replit auth not properly disabled")
                
        except Exception as e:
            self.log_error(f"Could not check auth configuration: {e}")
    
    def check_secrets_compliance(self):
        """Check that no secrets are hardcoded"""
        print("\n🔍 Checking secrets compliance...")
        
        try:
            with open('app.py', 'r') as f:
                content = f.read()
                
            # Check that hardcoded secrets were removed
            hardcoded_patterns = [
                '1015094007473-337qm1ofr5htlodjmsf2p6r3fcht6pg2.apps.googleusercontent.com',
                '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'
            ]
            
            for pattern in hardcoded_patterns:
                if pattern in content:
                    self.log_error(f"Hardcoded secret still present: {pattern[:20]}...")
                else:
                    self.log_fix("Hardcoded Google OAuth secrets removed")
                    
            # Check for proper environment variable usage
            if "os.environ.get('GOOGLE_CLIENT_ID')" in content:
                self.log_fix("Google OAuth using environment variables")
                self.secrets_needed.extend(['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET'])
            
        except Exception as e:
            self.log_error(f"Could not check secrets compliance: {e}")
    
    def check_public_routes(self):
        """Verify public routes are accessible"""
        print("\n🔍 Checking public routes...")
        
        try:
            with open('app.py', 'r') as f:
                content = f.read()
                
            if "@app.route('/')" in content:
                self.log_fix("Public landing page route configured")
            else:
                self.log_error("Public landing page route missing")
                
            if "def landing():" in content:
                self.log_fix("Landing page function implemented")
            else:
                self.log_error("Landing page function missing")
                
        except Exception as e:
            self.log_error(f"Could not check public routes: {e}")
    
    def check_health_endpoints(self):
        """Verify health endpoints are configured"""
        print("\n🔍 Checking health endpoints...")
        
        health_file = Path('routes/health_check.py')
        if health_file.exists():
            self.log_fix("Health check routes file exists")
            
            try:
                with open(health_file, 'r') as f:
                    content = f.read()
                    
                if "@health_bp.route('/health')" in content:
                    self.log_fix("/health endpoint configured")
                if "@health_bp.route('/healthz')" in content:
                    self.log_fix("/healthz endpoint configured")
                if "@health_bp.route('/ready')" in content:
                    self.log_fix("/ready endpoint configured")
                    
            except Exception as e:
                self.log_error(f"Could not read health check file: {e}")
        else:
            self.log_error("Health check routes file missing")
    
    def check_smoke_tests(self):
        """Verify smoke tests are configured"""
        print("\n🔍 Checking smoke test suite...")
        
        test_file = Path('tests/public_access_smoke_test.py')
        if test_file.exists():
            self.log_fix("Public access smoke test suite created")
        else:
            self.log_error("Smoke test suite missing")
    
    def validate_app_startup(self):
        """Test that the app can start without errors"""
        print("\n🔍 Testing application startup...")
        
        try:
            # Try importing the main app
            result = subprocess.run(
                [sys.executable, '-c', 'from app import create_app; app = create_app(); print("App startup successful")'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.log_fix("Application startup validation passed")
            else:
                self.log_error(f"Application startup failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            self.log_error("Application startup timed out")
        except Exception as e:
            self.log_error(f"Could not test app startup: {e}")
    
    def generate_final_report(self):
        """Generate comprehensive deployment report"""
        report = {
            'operation': 'PUBLIC-OR-BUST',
            'timestamp': datetime.now().isoformat(),
            'status': 'READY' if not self.errors else 'BLOCKED',
            'summary': {
                'fixes_applied': len(self.fixes_applied),
                'warnings': len(self.warnings),
                'errors': len(self.errors),
                'secrets_needed': len(self.secrets_needed)
            },
            'details': {
                'fixes_applied': self.fixes_applied,
                'warnings': self.warnings,
                'errors': self.errors,
                'secrets_needed': self.secrets_needed
            },
            'deployment_readiness': not self.errors
        }
        
        # Save report
        with open('OPERATION_PUBLIC_OR_BUST_REPORT.json', 'w') as f:
            json.dump(report, f, indent=2)
            
        return report
    
    def print_final_summary(self, report):
        """Print deployment summary"""
        print("\n" + "="*60)
        print("🚀 OPERATION PUBLIC-OR-BUST FINAL REPORT")
        print("="*60)
        
        status = "✅ DEPLOYMENT READY" if report['deployment_readiness'] else "❌ DEPLOYMENT BLOCKED"
        print(f"Status: {status}")
        print(f"Fixes Applied: {report['summary']['fixes_applied']}")
        print(f"Warnings: {report['summary']['warnings']}")
        print(f"Errors: {report['summary']['errors']}")
        
        if report['details']['secrets_needed']:
            print(f"\n🔑 SECRETS NEEDED in Replit Secrets:")
            for secret in report['details']['secrets_needed']:
                print(f"  • {secret}")
        
        if report['details']['errors']:
            print(f"\n💀 BLOCKING ERRORS:")
            for error in report['details']['errors']:
                print(f"  • {error}")
                
        if report['deployment_readiness']:
            print(f"\n🎉 READY FOR DEPLOYMENT!")
            print("Next steps:")
            print("1. Add required secrets to Replit Secrets")
            print("2. Click Deploy in Replit")
            print("3. Verify public access without login requirement")
        else:
            print(f"\n🔧 FIX REQUIRED before deployment")
            
        print("="*60)
    
    def run_validation(self):
        """Run complete validation suite"""
        print("💀 OPERATION PUBLIC-OR-BUST FINAL VALIDATION")
        print("="*60)
        
        self.check_proxy_configuration()
        self.check_session_security()
        self.check_auth_configuration()
        self.check_secrets_compliance()
        self.check_public_routes()
        self.check_health_endpoints()
        self.check_smoke_tests()
        self.validate_app_startup()
        
        report = self.generate_final_report()
        self.print_final_summary(report)
        
        return report['deployment_readiness']


def main():
    """Main validation runner"""
    validator = PublicDeploymentValidator()
    success = validator.run_validation()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()