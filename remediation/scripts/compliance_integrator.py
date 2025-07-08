#!/usr/bin/env python3
"""
Compliance and Integration Fixer
Run: python compliance_integrator.py
"""

import os
from pathlib import Path

class ComplianceIntegrator:
    def __init__(self):
        self.fixes_applied = 0
        
    def fix_all(self):
        print("🛡️ Fixing Compliance and Integrations...")
        
        # 1. HIPAA compliance
        self.implement_hipaa_compliance()
        
        # 2. GDPR compliance  
        self.implement_gdpr_compliance()
        
        # 3. Fix OAuth properly
        self.fix_oauth_implementation()
        
        # 4. Standardize integrations
        self.create_integration_framework()
        
        print(f"✅ Applied {self.fixes_applied} compliance and integration fixes!")

    def implement_hipaa_compliance(self):
        """Add HIPAA compliance features"""
        print("Implementing HIPAA compliance...")
        
        os.makedirs('src/compliance', exist_ok=True)
        
        hipaa_module = '''from datetime import datetime
from typing import Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)

class HIPAACompliance:
    """HIPAA compliance implementation"""
    
    def __init__(self):
        self.audit_logger = self._setup_audit_logger()
    
    def _setup_audit_logger(self):
        """Setup HIPAA audit logger"""
        audit_logger = logging.getLogger('hipaa_audit')
        handler = logging.FileHandler('/var/log/nous/hipaa_audit.log')
        formatter = logging.Formatter('%(asctime)s %(message)s')
        handler.setFormatter(formatter)
        audit_logger.addHandler(handler)
        audit_logger.setLevel(logging.INFO)
        return audit_logger
    
    def log_phi_access(self, user_id: str, resource: str, action: str, patient_id: Optional[str] = None):
        """Log all PHI access per HIPAA requirements"""
        from flask import request, session
        
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'resource': resource,
            'action': action,
            'patient_id': patient_id,
            'ip_address': request.remote_addr if request else None,
            'user_agent': request.headers.get('User-Agent') if request else None,
            'session_id': session.get('session_id') if session else None
        }
        
        self.audit_logger.info(json.dumps(log_entry))
    
    def encrypt_phi(self, data: str) -> str:
        """Encrypt Protected Health Information"""
        from utils.encryption import encryptor
        return encryptor.encrypt(data)
    
    def get_access_controls(self):
        """Get HIPAA access control definitions"""
        return {
            'patient': ['read_own', 'update_own'],
            'provider': ['read_assigned', 'update_assigned', 'create'],
            'admin': ['read_all', 'update_all', 'create', 'delete', 'audit']
        }
    
    def get_retention_policies(self):
        """Get HIPAA data retention policies"""
        return {
            'medical_records': 6 * 365,  # 6 years
            'audit_logs': 6 * 365,      # 6 years  
            'session_data': 30,         # 30 days
            'temp_files': 1,            # 1 day
        }

hipaa = HIPAACompliance()
'''
        
        with open('src/compliance/hipaa.py', 'w') as f:
            f.write(hipaa_module)
        
        self.fixes_applied += 1

    def implement_gdpr_compliance(self):
        """Add GDPR compliance features"""
        print("Implementing GDPR compliance...")
        
        gdpr_module = '''from typing import Dict, Any, List
import json
from datetime import datetime

class GDPRCompliance:
    """GDPR compliance implementation"""
    
    def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """Export all user data for GDPR requests"""
        return {
            'user_profile': self._get_user_profile(user_id),
            'mental_health_data': self._get_mental_health_data(user_id),
            'tasks_and_productivity': self._get_task_data(user_id),
            'family_data': self._get_family_data(user_id),
            'audit_logs': self._get_audit_logs(user_id),
            'export_timestamp': datetime.utcnow().isoformat()
        }
    
    def delete_user_data(self, user_id: str) -> bool:
        """Delete all user data per GDPR right to erasure"""
        try:
            from models import User, MoodEntry, Task, ThoughtRecord
            from app import db
            
            # Delete related data
            MoodEntry.query.filter_by(user_id=user_id).delete()
            Task.query.filter_by(user_id=user_id).delete()
            ThoughtRecord.query.filter_by(user_id=user_id).delete()
            
            # Anonymize user record
            user = User.query.get(user_id)
            if user:
                user.email = f"deleted_{user_id}@privacy.invalid"
                user.name = "Deleted User"
                user.is_active = False
                user.deleted_at = datetime.utcnow()
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False
    
    def update_consent(self, user_id: str, consent_type: str, granted: bool):
        """Update user consent preferences"""
        from models import Consent
        from app import db
        
        consent = Consent(
            user_id=user_id,
            consent_type=consent_type,
            granted=granted,
            timestamp=datetime.utcnow()
        )
        db.session.add(consent)
        db.session.commit()

gdpr = GDPRCompliance()
'''
        
        with open('src/compliance/gdpr.py', 'w') as f:
            f.write(gdpr_module)
        
        self.fixes_applied += 1

    def fix_oauth_implementation(self):
        """Fix OAuth security issues"""
        print("Fixing OAuth implementation...")
        
        oauth_fix = '''from authlib.integrations.flask_client import OAuth
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
'''
        
        with open('src/infrastructure/secure_oauth.py', 'w') as f:
            f.write(oauth_fix)
        
        self.fixes_applied += 1

    def create_integration_framework(self):
        """Standardize all third-party integrations"""
        print("Creating integration framework...")
        
        os.makedirs('src/infrastructure/integrations', exist_ok=True)
        
        integration_base = '''from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import requests
import logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class IntegrationError(Exception):
    """Integration-specific error"""
    pass

class IntegrationBase(ABC):
    """Base class for all third-party integrations"""
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create session with retry logic and timeouts"""
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504, 429]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session
    
    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the service"""
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """Check if service is available"""
        pass
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        try:
            response = self.session.request(
                method,
                f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}",
                timeout=30,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Integration request failed: {e}")
            raise IntegrationError(str(e))

class AIServiceIntegration(IntegrationBase):
    """Base for AI service integrations"""
    
    def count_tokens(self, text: str) -> int:
        """Estimate token count (override in subclasses)"""
        return len(text.split()) * 1.3  # Rough estimate
    
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate API cost (override in subclasses)"""
        return 0.0
'''
        
        with open('src/infrastructure/integrations/base.py', 'w') as f:
            f.write(integration_base)
        
        self.fixes_applied += 1

if __name__ == "__main__":
    fixer = ComplianceIntegrator()
    fixer.fix_all() 