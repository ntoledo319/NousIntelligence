"""
Environment Validation Module
Validates production environment configuration and provides graceful degradation
"""

import os
import logging
from typing import Dict, List, Tuple, Any

logger = logging.getLogger(__name__)

class EnvironmentValidator:
    """Validates environment configuration for production deployment"""
    
    def __init__(self):
        self.required_vars = [
            'SESSION_SECRET',
            'DATABASE_URL'
        ]
        self.optional_vars = [
            'GOOGLE_CLIENT_ID',
            'GOOGLE_CLIENT_SECRET',
            'TOKEN_ENCRYPTION_KEY'
        ]
        self.validation_results = {}
    
    def validate_all(self) -> Dict[str, Any]:
        """Perform comprehensive environment validation"""
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'missing_required': [],
            'missing_optional': [],
            'security_issues': [],
            'recommendations': []
        }
        
        # Check required environment variables
        for var in self.required_vars:
            value = os.environ.get(var)
            if not value:
                results['missing_required'].append(var)
                results['errors'].append(f"Required environment variable {var} is not set")
                results['valid'] = False
            else:
                # Validate specific requirements
                if var == 'SESSION_SECRET' and len(value) < 32:
                    results['security_issues'].append(f"{var} should be at least 32 characters for security")
                    results['valid'] = False
        
        # Check optional environment variables
        for var in self.optional_vars:
            value = os.environ.get(var)
            if not value:
                results['missing_optional'].append(var)
                results['warnings'].append(f"Optional environment variable {var} is not set")
        
        # Validate Google OAuth configuration
        oauth_validation = self._validate_oauth_config()
        if oauth_validation['errors']:
            results['errors'].extend(oauth_validation['errors'])
            results['valid'] = False
        if oauth_validation['warnings']:
            results['warnings'].extend(oauth_validation['warnings'])
        
        # Database validation
        db_validation = self._validate_database_config()
        if db_validation['errors']:
            results['errors'].extend(db_validation['errors'])
            results['valid'] = False
        if db_validation['warnings']:
            results['warnings'].extend(db_validation['warnings'])
        
        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(results)
        
        self.validation_results = results
        return results
    
    def _validate_oauth_config(self) -> Dict[str, List[str]]:
        """Validate Google OAuth configuration"""
        errors = []
        warnings = []
        
        client_id = os.environ.get('GOOGLE_CLIENT_ID')
        client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
        
        if client_id and client_secret:
            # Validate client ID format
            if not client_id.endswith('.apps.googleusercontent.com'):
                errors.append("GOOGLE_CLIENT_ID format appears invalid")
            
            # Validate client secret format
            if not client_secret.startswith('GOCSPX-'):
                errors.append("GOOGLE_CLIENT_SECRET format appears invalid")
        elif client_id or client_secret:
            # Only one is set
            errors.append("Both GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set together")
        else:
            warnings.append("Google OAuth not configured - authentication will be limited to demo mode")
        
        return {'errors': errors, 'warnings': warnings}
    
    def _validate_database_config(self) -> Dict[str, List[str]]:
        """Validate database configuration"""
        errors = []
        warnings = []
        
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            # Check for common database URL issues
            if database_url.startswith('postgres://'):
                warnings.append("DATABASE_URL uses deprecated 'postgres://' scheme, should use 'postgresql://'")
            elif not database_url.startswith(('postgresql://', 'sqlite:///')):
                errors.append("DATABASE_URL format not recognized")
        
        return {'errors': errors, 'warnings': warnings}
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate configuration recommendations based on validation results"""
        recommendations = []
        
        if results['missing_required']:
            recommendations.append("Set all required environment variables before deployment")
        
        if 'GOOGLE_CLIENT_ID' in results['missing_optional']:
            recommendations.append("Configure Google OAuth for full authentication features")
        
        if 'TOKEN_ENCRYPTION_KEY' in results['missing_optional']:
            recommendations.append("Set TOKEN_ENCRYPTION_KEY for enhanced security")
        
        if results['security_issues']:
            recommendations.append("Address security issues before production deployment")
        
        return recommendations
    
    def get_deployment_readiness(self) -> Tuple[bool, str]:
        """Check if application is ready for deployment"""
        if not self.validation_results:
            self.validate_all()
        
        results = self.validation_results
        
        if not results['valid']:
            return False, f"Deployment blocked: {len(results['errors'])} critical errors found"
        
        if len(results['warnings']) > 3:
            return True, f"Deployment ready with {len(results['warnings'])} warnings"
        
        return True, "Deployment ready - all checks passed"
    
    def get_graceful_degradation_config(self) -> Dict[str, bool]:
        """Get configuration for graceful feature degradation"""
        if not self.validation_results:
            self.validate_all()
        
        config = {
            'oauth_enabled': 'GOOGLE_CLIENT_ID' not in self.validation_results['missing_optional'],
            'token_encryption_enabled': 'TOKEN_ENCRYPTION_KEY' not in self.validation_results['missing_optional'],
            'demo_mode_available': True,  # Always available
            'secure_sessions': os.environ.get('SESSION_SECRET') is not None
        }
        
        return config

# Global validator instance
environment_validator = EnvironmentValidator()