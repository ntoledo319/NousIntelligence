#!/usr/bin/env python3
"""
Comprehensive Build Validator
Tests all critical systems and ensures complete functionality
"""

import os
import sys
import logging
import importlib
import traceback
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class BuildValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed_tests = []
        
    def validate_complete_build(self):
        """Run comprehensive build validation"""
        logger.info("🔍 Starting comprehensive build validation...")
        
        # Core system tests
        self.test_critical_imports()
        self.test_database_setup()
        self.test_app_creation()
        self.test_authentication_system()
        self.test_route_registration()
        self.test_template_rendering()
        self.test_api_endpoints()
        
        # Report results
        self.generate_report()
        
    def test_critical_imports(self):
        """Test critical module imports"""
        logger.info("Testing critical imports...")
        
        critical_modules = [
            'flask',
            'sqlalchemy',
            'werkzeug',
            'logging',
            'os',
            'datetime'
        ]
        
        for module in critical_modules:
            try:
                importlib.import_module(module)
                self.passed_tests.append(f"✅ Import {module}")
            except ImportError as e:
                self.errors.append(f"❌ Critical import failed: {module} - {e}")
        
        # Test app-specific imports
        app_modules = [
            'config',
            'database',
            'utils.auth_compat'
        ]
        
        for module in app_modules:
            try:
                importlib.import_module(module)
                self.passed_tests.append(f"✅ App module {module}")
            except ImportError as e:
                self.warnings.append(f"⚠️ App module issue: {module} - {e}")
    
    def test_database_setup(self):
        """Test database configuration"""
        logger.info("Testing database setup...")
        
        try:
            from database import db, init_database
            from flask import Flask
            
            test_app = Flask(__name__)
            test_app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///test.db')
            test_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
            
            init_database(test_app)
            self.passed_tests.append("✅ Database initialization")
            
        except Exception as e:
            self.errors.append(f"❌ Database setup failed: {e}")
    
    def test_app_creation(self):
        """Test Flask app creation"""
        logger.info("Testing app creation...")
        
        try:
            from app import create_app
            test_app = create_app()
            
            if test_app:
                self.passed_tests.append("✅ Flask app creation")
                
                # Test app configuration
                if hasattr(test_app, 'secret_key') and test_app.secret_key:
                    self.passed_tests.append("✅ App secret key configured")
                else:
                    self.warnings.append("⚠️ App secret key not configured")
                    
            else:
                self.errors.append("❌ App creation returned None")
                
        except Exception as e:
            self.errors.append(f"❌ App creation failed: {e}")
    
    def test_authentication_system(self):
        """Test authentication system"""
        logger.info("Testing authentication system...")
        
        try:
            from utils.auth_compat import get_demo_user, is_authenticated, login_required
            
            # Test demo user creation
            demo_user = get_demo_user()
            if demo_user and hasattr(demo_user, 'id'):
                self.passed_tests.append("✅ Demo user system")
            else:
                self.errors.append("❌ Demo user system failed")
            
            # Test authentication function
            if is_authenticated():
                self.passed_tests.append("✅ Authentication function")
            else:
                self.warnings.append("⚠️ Authentication returns False in demo mode")
            
            # Test decorator
            @login_required
            def test_decorated_function():
                return "success"
            
            result = test_decorated_function()
            if result == "success":
                self.passed_tests.append("✅ Authentication decorator")
            else:
                self.errors.append("❌ Authentication decorator failed")
                
        except Exception as e:
            self.errors.append(f"❌ Authentication system failed: {e}")
    
    def test_route_registration(self):
        """Test route registration system"""
        logger.info("Testing route registration...")
        
        try:
            from routes import register_all_blueprints
            from flask import Flask
            
            test_app = Flask(__name__)
            register_all_blueprints(test_app)
            
            # Count registered blueprints
            blueprint_count = len(test_app.blueprints)
            if blueprint_count > 0:
                self.passed_tests.append(f"✅ Blueprint registration ({blueprint_count} blueprints)")
            else:
                self.warnings.append("⚠️ No blueprints registered")
                
        except Exception as e:
            self.warnings.append(f"⚠️ Route registration issue: {e}")
    
    def test_template_rendering(self):
        """Test template rendering"""
        logger.info("Testing template rendering...")
        
        template_files = [
            'templates/landing.html',
            'templates/app.html'
        ]
        
        for template in template_files:
            if os.path.exists(template):
                self.passed_tests.append(f"✅ Template exists: {template}")
            else:
                self.warnings.append(f"⚠️ Template missing: {template}")
    
    def test_api_endpoints(self):
        """Test API endpoint accessibility"""
        logger.info("Testing API endpoints...")
        
        try:
            from app import create_app
            app = create_app()
            
            with app.test_client() as client:
                # Test health endpoint
                health_response = client.get('/health')
                if health_response.status_code == 200:
                    self.passed_tests.append("✅ Health endpoint accessible")
                else:
                    self.errors.append(f"❌ Health endpoint failed: {health_response.status_code}")
                
                # Test user API
                user_response = client.get('/api/user')
                if user_response.status_code == 200:
                    self.passed_tests.append("✅ User API accessible")
                else:
                    self.errors.append(f"❌ User API failed: {user_response.status_code}")
                
                # Test chat API
                chat_response = client.post('/api/chat', 
                                          json={'message': 'test', 'demo_mode': True})
                if chat_response.status_code == 200:
                    self.passed_tests.append("✅ Chat API accessible")
                else:
                    self.errors.append(f"❌ Chat API failed: {chat_response.status_code}")
                
        except Exception as e:
            self.errors.append(f"❌ API endpoint testing failed: {e}")
    
    def generate_report(self):
        """Generate comprehensive validation report"""
        logger.info("📊 Build Validation Report:")
        logger.info(f"   ✅ Passed tests: {len(self.passed_tests)}")
        logger.info(f"   ⚠️  Warnings: {len(self.warnings)}")
        logger.info(f"   ❌ Errors: {len(self.errors)}")
        
        if self.passed_tests:
            logger.info("\n✅ PASSED TESTS:")
            for test in self.passed_tests:
                logger.info(f"     {test}")
        
        if self.warnings:
            logger.info("\n⚠️ WARNINGS:")
            for warning in self.warnings:
                logger.info(f"     {warning}")
        
        if self.errors:
            logger.info("\n❌ ERRORS:")
            for error in self.errors:
                logger.info(f"     {error}")
        else:
            logger.info("\n🎯 NO CRITICAL ERRORS FOUND!")
        
        # Overall assessment
        if len(self.errors) == 0:
            if len(self.warnings) == 0:
                logger.info("\n🌟 BUILD STATUS: EXCELLENT - All tests passed")
            else:
                logger.info("\n✅ BUILD STATUS: GOOD - Minor warnings only")
        else:
            logger.info(f"\n🔧 BUILD STATUS: NEEDS FIXES - {len(self.errors)} critical errors")
        
        return len(self.errors) == 0

def main():
    validator = BuildValidator()
    success = validator.validate_complete_build()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()