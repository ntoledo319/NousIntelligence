from authlib.integrations.flask_client import OAuth
from flask import session, url_for, redirect, request
import secrets
import time
import os
from urllib.parse import urlparse

class SecureOAuth:
    def __init__(self, app):
        self.oauth = OAuth(app)
        self.setup_providers()
    
    def setup_providers(self):
        """Configure OAuth providers securely"""
        self.google = self.oauth.register(
            name='google',
            client_id=os.getenv('GOOGLE_CLIENT_ID'),
            client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={
                'scope': 'openid email profile',
                'token_endpoint_auth_method': 'client_secret_post'
            }
        )
    
    def generate_state_token(self) -> str:
        """Generate secure state token"""
        state = secrets.token_urlsafe(32)
        session['oauth_state'] = {
            'token': state,
            'expires': time.time() + 600,  # 10 minutes
            'nonce': secrets.token_urlsafe(16)
        }
        return state
    
    def verify_state_token(self, state: str) -> bool:
        """Verify state token"""
        stored_state = session.get('oauth_state')
        if not stored_state:
            return False
            
        if time.time() > stored_state['expires']:
            session.pop('oauth_state', None)
            return False
            
        if not secrets.compare_digest(state, stored_state['token']):
            return False
            
        session.pop('oauth_state', None)
        return True
    
    def validate_redirect_url(self, url: str) -> bool:
        """Validate redirect URLs against whitelist"""
        allowed_domains = os.getenv('ALLOWED_REDIRECT_DOMAINS', 'localhost,127.0.0.1').split(',')
        parsed = urlparse(url)
        return parsed.netloc in allowed_domains or parsed.netloc.endswith('.nous-platform.com')
