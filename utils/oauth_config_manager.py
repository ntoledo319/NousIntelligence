"""
OAuth Configuration Manager
Fixes Issues 18-20: Inconsistent OAuth checking, unused scopes, hardcoded URLs
"""

import os
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class OAuthConfig:
    """OAuth configuration with validation"""
    client_id: str
    client_secret: str
    redirect_uri: str
    scopes: List[str]
    authorization_base_url: str
    token_url: str
    userinfo_url: str
    issuer: str

class OAuthConfigManager:
    """Manages OAuth configuration with consistency checks"""
    
    def __init__(self):
        self.config = None
        self._load_config()
    
    def _load_config(self) -> None:
        """Load OAuth configuration from environment"""
        try:
            # Extract clean credentials
            client_id = self._extract_client_id()
            client_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '')
            
            if not client_id or not client_secret:
                logger.warning("OAuth credentials not fully configured")
                return
            
            # Determine redirect URI based on environment
            redirect_uri = self._get_redirect_uri()
            
            # Configure minimal required scopes only
            scopes = self._get_required_scopes()
            
            # Use configurable URLs (not hardcoded)
            urls = self._get_oauth_urls()
            
            self.config = OAuthConfig(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scopes=scopes,
                authorization_base_url=urls['auth'],
                token_url=urls['token'],
                userinfo_url=urls['userinfo'],
                issuer=urls['issuer']
            )
            
            logger.info("OAuth configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load OAuth configuration: {e}")
            self.config = None
    
    def _extract_client_id(self) -> str:
        """Extract clean client ID from potentially malformed environment variable"""
        client_id = os.environ.get('GOOGLE_CLIENT_ID', '')
        
        # Handle malformed client IDs from Replit environment
        if 'apps.googleusercontent.com' in client_id:
            # Extract just the ID part
            if '-' in client_id:
                parts = client_id.split('-')
                if parts[0].isdigit():
                    return client_id
        
        return client_id
    
    def _get_redirect_uri(self) -> str:
        """Get redirect URI based on deployment environment"""
        # Check for Replit deployment
        replit_url = os.environ.get('REPL_URL')
        if replit_url:
            return f"{replit_url}/auth/google/callback"
        
        # Check for custom domain
        domain = os.environ.get('CUSTOM_DOMAIN')
        if domain:
            return f"https://{domain}/auth/google/callback"
        
        # Development fallback
        return "http://localhost:5000/auth/google/callback"
    
    def _get_required_scopes(self) -> List[str]:
        """Get minimal required OAuth scopes (no unused scopes)"""
        # Only include scopes we actually use
        required_scopes = [
            'openid',
            'email',
            'profile'
        ]
        
        # Add optional scopes based on features enabled
        if os.environ.get('ENABLE_CALENDAR_INTEGRATION'):
            required_scopes.append('https://www.googleapis.com/auth/calendar.readonly')
        
        if os.environ.get('ENABLE_DRIVE_INTEGRATION'):
            required_scopes.append('https://www.googleapis.com/auth/drive.readonly')
        
        return required_scopes
    
    def _get_oauth_urls(self) -> Dict[str, str]:
        """Get OAuth URLs from configuration (not hardcoded)"""
        base_url = os.environ.get('GOOGLE_OAUTH_BASE_URL', 'https://accounts.google.com')
        api_base = os.environ.get('GOOGLE_API_BASE_URL', 'https://www.googleapis.com')
        
        return {
            'auth': f"{base_url}/o/oauth2/v2/auth",
            'token': f"{base_url}/o/oauth2/token",
            'userinfo': f"{api_base}/oauth2/v2/userinfo",
            'issuer': base_url
        }
    
    def is_configured(self) -> bool:
        """Check if OAuth is properly configured"""
        return self.config is not None
    
    def get_config(self) -> Optional[OAuthConfig]:
        """Get current OAuth configuration"""
        return self.config
    
    def get_client_config(self) -> Dict[str, Any]:
        """Get client configuration for OAuth library"""
        if not self.config:
            return {}
        
        return {
            'client_id': self.config.client_id,
            'client_secret': self.config.client_secret,
            'server_metadata_url': f"{self.config.issuer}/.well-known/openid_configuration",
            'client_kwargs': {
                'scope': ' '.join(self.config.scopes),
                'redirect_uri': self.config.redirect_uri
            }
        }
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate OAuth configuration consistency"""
        validation_result = {
            'valid': False,
            'issues': [],
            'warnings': []
        }
        
        if not self.config:
            validation_result['issues'].append("OAuth configuration not loaded")
            return validation_result
        
        # Validate client credentials
        if not self.config.client_id or len(self.config.client_id) < 10:
            validation_result['issues'].append("Invalid or missing client ID")
        
        if not self.config.client_secret or len(self.config.client_secret) < 10:
            validation_result['issues'].append("Invalid or missing client secret")
        
        # Validate redirect URI
        if not self.config.redirect_uri or not self.config.redirect_uri.startswith(('http://', 'https://')):
            validation_result['issues'].append("Invalid redirect URI")
        
        # Validate scopes
        if not self.config.scopes or 'openid' not in self.config.scopes:
            validation_result['issues'].append("Missing required OpenID scope")
        
        # Check for unused scopes
        unused_scopes = self._check_unused_scopes()
        if unused_scopes:
            validation_result['warnings'].append(f"Unused scopes detected: {', '.join(unused_scopes)}")
        
        # Validate URLs
        required_urls = ['authorization_base_url', 'token_url', 'userinfo_url']
        for url_field in required_urls:
            url = getattr(self.config, url_field)
            if not url or not url.startswith('https://'):
                validation_result['issues'].append(f"Invalid {url_field}")
        
        validation_result['valid'] = len(validation_result['issues']) == 0
        return validation_result
    
    def _check_unused_scopes(self) -> List[str]:
        """Check for potentially unused OAuth scopes"""
        if not self.config:
            return []
        
        # Define scopes and their usage indicators
        scope_usage = {
            'https://www.googleapis.com/auth/calendar': 'ENABLE_CALENDAR_INTEGRATION',
            'https://www.googleapis.com/auth/drive': 'ENABLE_DRIVE_INTEGRATION',
            'https://www.googleapis.com/auth/gmail.readonly': 'ENABLE_GMAIL_INTEGRATION',
            'https://www.googleapis.com/auth/tasks': 'ENABLE_TASKS_INTEGRATION'
        }
        
        unused = []
        for scope in self.config.scopes:
            if scope in scope_usage:
                env_var = scope_usage[scope]
                if not os.environ.get(env_var):
                    unused.append(scope)
        
        return unused
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get OAuth configuration status summary"""
        if not self.config:
            return {
                'configured': False,
                'status': 'not_configured',
                'message': 'OAuth configuration not loaded'
            }
        
        validation = self.validate_configuration()
        
        return {
            'configured': True,
            'valid': validation['valid'],
            'status': 'valid' if validation['valid'] else 'invalid',
            'client_id_configured': bool(self.config.client_id),
            'redirect_uri': self.config.redirect_uri,
            'scopes_count': len(self.config.scopes),
            'issues_count': len(validation['issues']),
            'warnings_count': len(validation['warnings']),
            'message': 'OAuth properly configured' if validation['valid'] else f"{len(validation['issues'])} configuration issues found"
        }

# Global configuration manager instance
oauth_config_manager = OAuthConfigManager()