#!/usr/bin/env python3
"""
NOUS Deployment Verification Tool

This script verifies that the application is ready for deployment by checking:
1. Environment variables
2. Database connection
3. Required files
4. Permissions

Usage:
  python verify_deployment.py

Returns exit code 0 if all checks pass, 1 otherwise.
"""

import os
import sys
import logging
import json
from pathlib import Path
import importlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('verify_deployment')

class DeploymentVerifier:
    """Class to verify deployment readiness"""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.passed = []
    
    def check_environment_variables(self):
        """Check if required environment variables are set"""
        logger.info("Checking environment variables...")
        
        # Critical variables - deployment will fail without these
        critical_vars = ['DATABASE_URL']
        for var in critical_vars:
            if os.environ.get(var):
                self.passed.append(f"✓ Environment variable {var} is set")
            else:
                self.issues.append(f"✗ Critical environment variable {var} is not set")
        
        # Check that at least one of SECRET_KEY or SESSION_SECRET is set
        if os.environ.get('SECRET_KEY') or os.environ.get('SESSION_SECRET'):
            self.passed.append("✓ Secret key is configured")
        else:
            self.issues.append("✗ Neither SECRET_KEY nor SESSION_SECRET is set")
        
        # Optional but recommended variables
        optional_vars = ['FLASK_ENV', 'GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 
                         'GOOGLE_REDIRECT_URI', 'SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_SECRET']
        for var in optional_vars:
            if os.environ.get(var):
                self.passed.append(f"✓ Optional environment variable {var} is set")
            else:
                self.warnings.append(f"! Optional environment variable {var} is not set")
    
    def check_database_connection(self):
        """Check database connection"""
        logger.info("Checking database connection...")
        
        if not os.environ.get('DATABASE_URL'):
            self.issues.append("✗ Cannot check database connection - DATABASE_URL not set")
            return
        
        try:
            import psycopg2
            conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()
            conn.close()
            
            version_str = "Unknown version"
            if db_version is not None:
                if len(db_version) > 0 and db_version[0] is not None:
                    version_parts = str(db_version[0]).split(',')
                    if len(version_parts) > 0:
                        version_str = version_parts[0]
                
            self.passed.append(f"✓ Database connection successful: {version_str}")
        except ImportError:
            self.issues.append("✗ psycopg2 module not installed - required for database connection")
        except Exception as e:
            self.issues.append(f"✗ Database connection failed: {str(e)}")
    
    def check_required_files(self):
        """Check if required files exist"""
        logger.info("Checking required files...")
        
        required_files = [
            ('main.py', "Main application entry point"),
            ('app_factory.py', "Application factory"),
            ('gunicorn_config.py', "Gunicorn configuration"),
            ('start.sh', "Startup script"),
            ('models.py', "Database models"),
            ('config.py', "Configuration module")
        ]
        
        for filename, description in required_files:
            if os.path.isfile(filename):
                self.passed.append(f"✓ {description} ({filename}) exists")
            else:
                self.issues.append(f"✗ {description} ({filename}) is missing")
    
    def check_directory_permissions(self):
        """Check directory permissions"""
        logger.info("Checking directory permissions...")
        
        required_dirs = [
            ('flask_session', "Session storage"),
            ('uploads', "File uploads"),
            ('logs', "Log files"),
            ('instance', "Instance directory")
        ]
        
        for dirname, description in required_dirs:
            # Create directory if it doesn't exist
            os.makedirs(dirname, exist_ok=True)
            
            # Check if directory is writable
            if os.access(dirname, os.W_OK):
                self.passed.append(f"✓ {description} directory ({dirname}) is writable")
            else:
                self.issues.append(f"✗ {description} directory ({dirname}) is not writable")
    
    def check_code_imports(self):
        """Check if code imports are valid"""
        logger.info("Checking code imports...")
        
        try:
            # Import key modules to ensure they're available
            import flask
            import gunicorn
            import sqlalchemy
            
            self.passed.append("✓ Core dependencies (Flask, Gunicorn, SQLAlchemy) are installed")
        except ImportError as e:
            self.issues.append(f"✗ Core dependency missing: {str(e)}")
        
        # Try importing our own modules
        modules_to_check = [
            ('app_factory', "Application factory"),
            ('config', "Configuration module"),
            ('models', "Database models")
        ]
        
        for module_name, description in modules_to_check:
            try:
                importlib.import_module(module_name)
                self.passed.append(f"✓ {description} module imports successfully")
            except ImportError as e:
                self.issues.append(f"✗ {description} module cannot be imported: {str(e)}")
            except Exception as e:
                self.issues.append(f"✗ Error importing {description} module: {str(e)}")
    
    def run_all_checks(self):
        """Run all deployment verification checks"""
        logger.info("Starting deployment verification...")
        
        checks = [
            self.check_environment_variables,
            self.check_database_connection,
            self.check_required_files,
            self.check_directory_permissions,
            self.check_code_imports
        ]
        
        for check_func in checks:
            try:
                check_func()
            except Exception as e:
                self.issues.append(f"✗ Error during {check_func.__name__}: {str(e)}")
        
        # Print summary
        print("\n=== DEPLOYMENT VERIFICATION SUMMARY ===\n")
        
        if self.issues:
            print("CRITICAL ISSUES:")
            for issue in self.issues:
                print(f"  {issue}")
            print()
        
        if self.warnings:
            print("WARNINGS:")
            for warning in self.warnings:
                print(f"  {warning}")
            print()
        
        if self.passed:
            print("PASSED CHECKS:")
            for passed in self.passed:
                print(f"  {passed}")
            print()
        
        # Overall result
        if self.issues:
            print("\n❌ VERIFICATION FAILED: Please resolve the critical issues before deploying.")
            return False
        elif self.warnings:
            print("\n⚠️ VERIFICATION PASSED WITH WARNINGS: The application can be deployed, but some improvements are recommended.")
            return True
        else:
            print("\n✅ VERIFICATION PASSED: The application is ready for deployment.")
            return True

if __name__ == "__main__":
    verifier = DeploymentVerifier()
    success = verifier.run_all_checks()
    
    sys.exit(0 if success else 1)