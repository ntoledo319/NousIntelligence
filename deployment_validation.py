#!/usr/bin/env python3
"""
Deployment Validation Script
Based on Replit deployment playbook best practices
"""
import os
import sys
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

class DeploymentValidator:
    def __init__(self):
        self.issues = []
        self.fixes_applied = []
        self.report = {
            'timestamp': datetime.now().isoformat(),
            'status': 'unknown',
            'files_checked': [],
            'issues_found': [],
            'fixes_applied': [],
            'health_check_result': None
        }
    
    def log_issue(self, category, description, severity='warning'):
        """Log a deployment issue"""
        issue = {
            'category': category,
            'description': description,
            'severity': severity,
            'timestamp': datetime.now().isoformat()
        }
        self.issues.append(issue)
        self.report['issues_found'].append(issue)
        print(f"⚠️  {severity.upper()}: {description}")
    
    def log_fix(self, description):
        """Log a fix that was applied"""
        fix = {
            'description': description,
            'timestamp': datetime.now().isoformat()
        }
        self.fixes_applied.append(fix)
        self.report['fixes_applied'].append(fix)
        print(f"✅ FIX: {description}")
    
    def check_port_configuration(self):
        """Validate port configuration follows best practices"""
        print("\n🔍 Checking port configuration...")
        
        # Check main.py
        main_py = Path('main.py')
        if main_py.exists():
            content = main_py.read_text()
            if ('os.environ.get' in content and 'PORT' in content) or \
               ('from config import' in content and 'PORT' in content):
                print("✅ main.py uses proper port configuration")
            else:
                self.log_issue('port', 'main.py may have hardcoded port', 'error')
        
        # Check config files
        config_path = Path('config/app_config.py')
        if config_path.exists():
            content = config_path.read_text()
            if 'int(os.environ.get(\'PORT\'' in content:
                print("✅ Configuration properly uses PORT environment variable")
            else:
                self.log_issue('port', 'Configuration missing proper PORT env var usage', 'warning')
    
    def check_secret_exposure(self):
        """Check for exposed secrets"""
        print("\n🔍 Checking for exposed secrets...")
        
        sensitive_files = [
            'replit.toml', 'app.py', 'config/app_config.py', 
            '.env', 'requirements.txt', 'pyproject.toml'
        ]
        
        for file_name in sensitive_files:
            file_path = Path(file_name)
            if file_path.exists():
                content = file_path.read_text()
                
                # Check for exposed secrets
                secret_patterns = ['api_key', 'secret_key', 'password', 'token', 'client_secret']
                for pattern in secret_patterns:
                    if pattern in content.lower():
                        # Check if it's properly using environment variables
                        if 'os.environ' in content or 'getenv' in content:
                            print(f"✅ {file_name} properly uses environment variables for secrets")
                        else:
                            # Check if it's just a comment or documentation
                            lines_with_pattern = [line for line in content.split('\n') 
                                                if pattern in line.lower() and not line.strip().startswith('#')]
                            if lines_with_pattern:
                                self.log_issue('security', f'Potential secret exposure in {file_name}', 'critical')
                            else:
                                print(f"✅ {file_name} references secrets safely in comments")
                        break
    
    def check_dependency_health(self):
        """Check dependency health"""
        print("\n🔍 Checking dependency health...")
        
        try:
            # Test core imports
            import flask
            import werkzeug
            import sqlalchemy
            print("✅ Core dependencies import successfully")
            
            # Check pyproject.toml for conflicts
            pyproject = Path('pyproject.toml')
            if pyproject.exists():
                print("✅ pyproject.toml exists")
                self.report['files_checked'].append('pyproject.toml')
            else:
                self.log_issue('dependencies', 'Missing pyproject.toml', 'warning')
                
        except ImportError as e:
            self.log_issue('dependencies', f'Import error: {str(e)}', 'critical')
    
    def test_application_startup(self):
        """Test if application can start without errors"""
        print("\n🔍 Testing application startup...")
        
        try:
            # Import the app
            from app import app
            
            # Test basic configuration
            if app.config.get('SECRET_KEY'):
                print("✅ Application has secret key configured")
            else:
                self.log_issue('config', 'Missing secret key configuration', 'error')
            
            # Test route registration
            routes = [rule.rule for rule in app.url_map.iter_rules()]
            if '/health' in routes or '/healthz' in routes:
                print("✅ Health endpoint is registered")
            else:
                self.log_issue('health', 'Missing health endpoint', 'error')
            
            print("✅ Application startup test passed")
            
        except Exception as e:
            self.log_issue('startup', f'Application startup failed: {str(e)}', 'critical')
    
    def test_health_endpoint(self):
        """Test health endpoint functionality"""
        print("\n🔍 Testing health endpoint...")
        
        try:
            from app import app
            
            with app.test_client() as client:
                # Test /health endpoint
                response = client.get('/health')
                if response.status_code == 200:
                    print("✅ /health endpoint returns 200")
                    self.report['health_check_result'] = {
                        'endpoint': '/health',
                        'status_code': response.status_code,
                        'response': response.get_json()
                    }
                else:
                    self.log_issue('health', f'/health endpoint returns {response.status_code}', 'error')
                
                # Test /healthz endpoint
                response = client.get('/healthz')
                if response.status_code == 200:
                    print("✅ /healthz endpoint returns 200")
                else:
                    self.log_issue('health', f'/healthz endpoint returns {response.status_code}', 'error')
                    
        except Exception as e:
            self.log_issue('health', f'Health endpoint test failed: {str(e)}', 'error')
    
    def generate_report(self):
        """Generate final deployment validation report"""
        print("\n" + "="*60)
        print("🎯 DEPLOYMENT VALIDATION REPORT")
        print("="*60)
        
        # Determine overall status
        critical_issues = [i for i in self.issues if i['severity'] == 'critical']
        error_issues = [i for i in self.issues if i['severity'] == 'error']
        
        if critical_issues:
            self.report['status'] = 'failed'
            status_icon = "❌"
        elif error_issues:
            self.report['status'] = 'warning'
            status_icon = "⚠️"
        else:
            self.report['status'] = 'passed'
            status_icon = "✅"
        
        print(f"\n{status_icon} Overall Status: {self.report['status'].upper()}")
        print(f"📊 Issues Found: {len(self.issues)}")
        print(f"🔧 Fixes Applied: {len(self.fixes_applied)}")
        
        if self.issues:
            print(f"\n📋 Issues Summary:")
            for issue in self.issues:
                print(f"  • {issue['severity'].upper()}: {issue['description']}")
        
        if self.fixes_applied:
            print(f"\n🔧 Fixes Applied:")
            for fix in self.fixes_applied:
                print(f"  • {fix['description']}")
        
        # Save report to file
        report_path = Path('deployment_validation_report.json')
        with open(report_path, 'w') as f:
            json.dump(self.report, f, indent=2)
        
        print(f"\n📄 Full report saved to: {report_path}")
        
        return self.report['status'] == 'passed'

def main():
    """Run deployment validation"""
    print("🚀 DEPLOYMENT VALIDATION STARTING")
    print("Following Replit deployment playbook best practices...")
    
    validator = DeploymentValidator()
    
    # Run all validation checks
    validator.check_port_configuration()
    validator.check_secret_exposure()
    validator.check_dependency_health()
    validator.test_application_startup()
    validator.test_health_endpoint()
    
    # Generate final report
    success = validator.generate_report()
    
    if success:
        print("\n🎉 DEPLOYMENT VALIDATION PASSED - Ready for deployment!")
        return 0
    else:
        print("\n🚨 DEPLOYMENT VALIDATION FAILED - Fix issues before deploying")
        return 1

if __name__ == '__main__':
    sys.exit(main())