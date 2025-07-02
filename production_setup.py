#!/usr/bin/env python3
"""
NOUS Production Setup Script
Automated production deployment and validation
"""

import os
import sys
import subprocess
import json
import time
import secrets
import urllib.request
import urllib.error
from pathlib import Path

class ProductionSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.env_file = self.project_root / '.env'
        self.status = {
            'dependencies': False,
            'environment': False,
            'database': False,
            'application': False,
            'health_check': False
        }
    
    def log(self, message, level="INFO"):
        """Enhanced logging with timestamps"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        colors = {
            "INFO": "\033[94m",    # Blue
            "SUCCESS": "\033[92m", # Green
            "WARNING": "\033[93m", # Yellow
            "ERROR": "\033[91m",   # Red
            "RESET": "\033[0m"     # Reset
        }
        color = colors.get(level, colors["INFO"])
        print(f"{color}[{timestamp}] {level}: {message}{colors['RESET']}")
    
    def generate_secure_key(self, length=64):
        """Generate cryptographically secure random key"""
        return secrets.token_urlsafe(length)
    
    def check_python_version(self):
        """Verify Python version compatibility"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 11):
            self.log("Python 3.11+ required. Current version: {}.{}.{}".format(
                version.major, version.minor, version.micro), "ERROR")
            return False
        self.log(f"Python version {version.major}.{version.minor}.{version.micro} - Compatible ✅", "SUCCESS")
        return True
    
    def install_dependencies(self):
        """Install required Python packages"""
        self.log("Installing dependencies...", "INFO")
        try:
            # Check if pyproject.toml exists
            if (self.project_root / 'pyproject.toml').exists():
                subprocess.run([sys.executable, '-m', 'pip', 'install', '-e', '.', '--break-system-packages'], 
                             check=True, cwd=self.project_root, capture_output=True)
            else:
                # Fallback to manual installation
                packages = [
                    'flask>=3.1.1', 'werkzeug>=3.1.3', 'gunicorn>=22.0.0',
                    'flask-sqlalchemy>=3.1.1', 'flask-migrate>=4.0.7', 'flask-login>=0.6.3',
                    'psycopg2-binary>=2.9.9', 'authlib>=1.3.0', 'flask-session>=0.8.0',
                    'python-dotenv>=1.0.1', 'requests>=2.32.3', 'psutil>=5.9.8'
                ]
                subprocess.run([sys.executable, '-m', 'pip', 'install', '--break-system-packages'] + packages,
                             check=True, capture_output=True)
            
            self.status['dependencies'] = True
            self.log("Dependencies installed successfully ✅", "SUCCESS")
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"Failed to install dependencies: {e}", "ERROR")
            return False
    
    def setup_environment(self, production=False):
        """Setup environment variables for development or production"""
        self.log("Setting up environment configuration...", "INFO")
        
        env_vars = {}
        
        # Check existing environment variables
        existing_session_secret = os.environ.get('SESSION_SECRET')
        existing_db_url = os.environ.get('DATABASE_URL')
        existing_google_id = os.environ.get('GOOGLE_CLIENT_ID')
        existing_google_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
        
        # Generate secure session secret if not exists
        if not existing_session_secret or len(existing_session_secret) < 32:
            env_vars['SESSION_SECRET'] = self.generate_secure_key(48)
            self.log("Generated secure SESSION_SECRET", "SUCCESS")
        else:
            env_vars['SESSION_SECRET'] = existing_session_secret
            self.log("Using existing SESSION_SECRET", "INFO")
        
        # Database configuration
        if not existing_db_url:
            if production:
                self.log("PRODUCTION: Please set DATABASE_URL manually for PostgreSQL", "WARNING")
                env_vars['DATABASE_URL'] = "postgresql://user:pass@localhost:5432/nous_prod"
            else:
                env_vars['DATABASE_URL'] = "sqlite:///nous_dev.db"
                self.log("Using SQLite for development", "INFO")
        else:
            env_vars['DATABASE_URL'] = existing_db_url
        
        # Google OAuth configuration
        if not existing_google_id or not existing_google_secret:
            if production:
                self.log("PRODUCTION: Please set Google OAuth credentials manually", "WARNING")
                env_vars['GOOGLE_CLIENT_ID'] = "your-google-client-id"
                env_vars['GOOGLE_CLIENT_SECRET'] = "your-google-client-secret"
            else:
                env_vars['GOOGLE_CLIENT_ID'] = f"dev-client-id-{self.generate_secure_key(16)}"
                env_vars['GOOGLE_CLIENT_SECRET'] = self.generate_secure_key(48)
                self.log("Generated development OAuth credentials", "INFO")
        else:
            env_vars['GOOGLE_CLIENT_ID'] = existing_google_id
            env_vars['GOOGLE_CLIENT_SECRET'] = existing_google_secret
        
        # Optional security enhancement
        if not os.environ.get('TOKEN_ENCRYPTION_KEY'):
            env_vars['TOKEN_ENCRYPTION_KEY'] = self.generate_secure_key(32)
            self.log("Generated TOKEN_ENCRYPTION_KEY for enhanced security", "SUCCESS")
        
        # Set environment variables
        for key, value in env_vars.items():
            os.environ[key] = value
        
        # Create .env file for persistence
        try:
            with open(self.env_file, 'w') as f:
                f.write("# NOUS Environment Configuration\n")
                f.write(f"# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                for key, value in env_vars.items():
                    f.write(f"{key}={value}\n")
            self.log(f"Environment file created: {self.env_file}", "SUCCESS")
        except Exception as e:
            self.log(f"Warning: Could not create .env file: {e}", "WARNING")
        
        self.status['environment'] = True
        return True
    
    def test_application_import(self):
        """Test if the application can be imported and created"""
        self.log("Testing application import...", "INFO")
        try:
            # Test basic import
            import app
            self.log("App module imported successfully", "SUCCESS")
            
            # Test app creation
            flask_app = app.create_app()
            self.log("Flask application created successfully", "SUCCESS")
            
            with flask_app.app_context():
                from database import db
                db.create_all()
                self.log("Database tables created", "SUCCESS")
            
            self.status['application'] = True
            self.status['database'] = True
            return True
        except Exception as e:
            self.log(f"Application import failed: {e}", "ERROR")
            return False
    
    def start_application(self, background=True):
        """Start the application server"""
        self.log("Starting application server...", "INFO")
        try:
            if background:
                # Start in background
                proc = subprocess.Popen([sys.executable, 'main.py'], 
                                      cwd=self.project_root,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
                time.sleep(3)  # Give it time to start
                if proc.poll() is None:  # Still running
                    self.log("Application started in background", "SUCCESS")
                    return proc
                else:
                    stdout, stderr = proc.communicate()
                    self.log(f"Application failed to start: {stderr.decode()}", "ERROR")
                    return None
            else:
                # Start in foreground
                subprocess.run([sys.executable, 'main.py'], cwd=self.project_root)
        except Exception as e:
            self.log(f"Failed to start application: {e}", "ERROR")
            return None
    
    def health_check(self, max_retries=5):
        """Perform comprehensive health check"""
        self.log("Performing health check...", "INFO")
        
        for attempt in range(max_retries):
            try:
                # Check main page
                with urllib.request.urlopen('http://localhost:8080/') as response:
                    if response.status == 200:
                        self.log("Main page accessible ✅", "SUCCESS")
                        break
            except urllib.error.URLError:
                if attempt < max_retries - 1:
                    self.log(f"Health check attempt {attempt + 1} failed, retrying...", "WARNING")
                    time.sleep(2)
                else:
                    self.log("Main page health check failed", "ERROR")
                    return False
        
        # Check API health endpoint
        try:
            with urllib.request.urlopen('http://localhost:8080/api/health') as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    self.log("API health endpoint accessible ✅", "SUCCESS")
                    
                    # Parse health status
                    if data.get('status') in ['healthy', 'unhealthy']:
                        checks = data.get('checks', {})
                        for check_name, check_data in checks.items():
                            status = "✅" if check_data.get('healthy') else "⚠️"
                            self.log(f"  {check_name}: {status}", "INFO")
                    
                    self.status['health_check'] = True
                    return True
        except Exception as e:
            self.log(f"API health check failed: {e}", "ERROR")
            return False
    
    def generate_deployment_summary(self):
        """Generate deployment summary report"""
        total_checks = len(self.status)
        passed_checks = sum(self.status.values())
        success_rate = (passed_checks / total_checks) * 100
        
        self.log("=" * 60, "INFO")
        self.log("DEPLOYMENT SUMMARY", "INFO")
        self.log("=" * 60, "INFO")
        
        for check, status in self.status.items():
            status_icon = "✅" if status else "❌"
            self.log(f"{check.upper()}: {status_icon}", "SUCCESS" if status else "ERROR")
        
        self.log(f"Overall Success Rate: {success_rate:.1f}%", "SUCCESS" if success_rate >= 80 else "WARNING")
        
        if success_rate >= 80:
            self.log("🚀 DEPLOYMENT SUCCESSFUL! Application ready for production.", "SUCCESS")
            self.log("Access your application at: http://localhost:8080", "INFO")
            self.log("API Health: http://localhost:8080/api/health", "INFO")
        else:
            self.log("❌ Deployment needs attention. Check errors above.", "ERROR")
        
        return success_rate >= 80
    
    def run_full_setup(self, production=False):
        """Run complete production setup process"""
        self.log("🚀 Starting NOUS Production Setup", "INFO")
        self.log(f"Mode: {'PRODUCTION' if production else 'DEVELOPMENT'}", "INFO")
        
        # Step 1: Check Python version
        if not self.check_python_version():
            return False
        
        # Step 2: Install dependencies
        if not self.install_dependencies():
            return False
        
        # Step 3: Setup environment
        if not self.setup_environment(production=production):
            return False
        
        # Step 4: Test application
        if not self.test_application_import():
            return False
        
        # Step 5: Start application
        app_process = self.start_application(background=True)
        if not app_process:
            return False
        
        # Step 6: Health check
        health_ok = self.health_check()
        
        # Step 7: Generate summary
        success = self.generate_deployment_summary()
        
        if success:
            self.log("Setup completed successfully! 🎉", "SUCCESS")
            if production:
                self.log("PRODUCTION NOTES:", "WARNING")
                self.log("1. Update Google OAuth credentials in environment", "WARNING")
                self.log("2. Configure production database (PostgreSQL)", "WARNING")
                self.log("3. Set up monitoring and backups", "WARNING")
        
        return success

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='NOUS Production Setup')
    parser.add_argument('--production', action='store_true', 
                       help='Configure for production deployment')
    parser.add_argument('--development', action='store_true', 
                       help='Configure for development (default)')
    
    args = parser.parse_args()
    
    production_mode = args.production
    
    setup = ProductionSetup()
    success = setup.run_full_setup(production=production_mode)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()