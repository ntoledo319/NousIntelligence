"""
Enhanced Authentication Service
Consolidates all authentication functionality with security optimization
"""

import os
import jwt
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from werkzeug.security import generate_password_hash, check_password_hash

logger = logging.getLogger(__name__)

class EnhancedAuthService:
    """Enhanced authentication service with security optimization"""
    
    def __init__(self):
        self.secret_key = os.environ.get('SESSION_SECRET')
        if not self.secret_key:
            raise ValueError("SESSION_SECRET environment variable is required for authentication service")
        if len(self.secret_key) < 32:
            raise ValueError("SESSION_SECRET must be at least 32 characters long for security")
        self.token_expiry = timedelta(hours=24)
        self.failed_attempts = {}
        self._initialize_security()
    
    def _initialize_security(self):
        """Initialize security components"""
        try:
            # Initialize security components
            self.security_initialized = True
            logger.info("Enhanced auth service initialized")
        except Exception as e:
            logger.error(f"Auth service initialization error: {e}")
            self.security_initialized = False
    
    def generate_token(self, user_id: str, additional_claims: Dict = None) -> str:
        """Generate JWT token with enhanced security"""
        try:
            payload = {
                'user_id': user_id,
                'exp': datetime.utcnow() + self.token_expiry,
                'iat': datetime.utcnow(),
                'iss': 'nous-cbt-system'
            }
            
            if additional_claims:
                payload.update(additional_claims)
            
            token = jwt.encode(payload, self.secret_key, algorithm='HS256')
            return token
            
        except Exception as e:
            logger.error(f"Token generation error: {e}")
            return None
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token with enhanced validation"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return {
                'valid': True,
                'user_id': payload.get('user_id'),
                'claims': payload
            }
        except jwt.ExpiredSignatureError:
            return {'valid': False, 'error': 'Token expired'}
        except jwt.InvalidTokenError as e:
            return {'valid': False, 'error': f'Invalid token: {e}'}
    
    def hash_password(self, password: str) -> str:
        """Hash password with enhanced security"""
        return generate_password_hash(password)
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password with enhanced security"""
        return check_password_hash(password_hash, password)
    
    def track_failed_attempt(self, identifier: str):
        """Track failed authentication attempts"""
        if identifier not in self.failed_attempts:
            self.failed_attempts[identifier] = {'count': 0, 'last_attempt': datetime.now()}
        
        self.failed_attempts[identifier]['count'] += 1
        self.failed_attempts[identifier]['last_attempt'] = datetime.now()
    
    def is_locked_out(self, identifier: str, max_attempts: int = 5, lockout_duration: int = 300) -> bool:
        """Check if account is locked out"""
        if identifier not in self.failed_attempts:
            return False
        
        attempts = self.failed_attempts[identifier]
        if attempts['count'] >= max_attempts:
            time_since_last = (datetime.now() - attempts['last_attempt']).seconds
            return time_since_last < lockout_duration
        
        return False
    
    def clear_failed_attempts(self, identifier: str):
        """Clear failed attempts for successful login"""
        if identifier in self.failed_attempts:
            del self.failed_attempts[identifier]
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get security service status"""
        return {
            'security_initialized': self.security_initialized,
            'active_lockouts': len([k for k, v in self.failed_attempts.items() 
                                  if self.is_locked_out(k)]),
            'total_tracked_attempts': len(self.failed_attempts),
            'status': 'secure' if self.security_initialized else 'degraded'
        }

# Global instance
enhanced_auth_service = EnhancedAuthService()

# Backward compatibility functions
def generate_user_token(user_id: str, **kwargs) -> str:
    """Generate user token - backward compatible"""
    return enhanced_auth_service.generate_token(user_id, kwargs)

def verify_user_token(token: str) -> Dict[str, Any]:
    """Verify user token - backward compatible"""
    return enhanced_auth_service.verify_token(token)
