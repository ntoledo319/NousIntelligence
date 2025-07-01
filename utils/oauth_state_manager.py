"""
OAuth State Management
Implements secure OAuth state validation with HMAC and fingerprinting
"""

import hmac
import hashlib
import base64
import secrets
import logging
from datetime import datetime, timedelta
from flask import session

logger = logging.getLogger(__name__)

class OAuthStateManager:
    """Secure OAuth state management with HMAC validation"""
    
    def __init__(self, secret_key):
        self.secret_key = secret_key.encode('utf-8') if isinstance(secret_key, str) else secret_key
        self.state_timeout = 600  # 10 minutes
    
    def generate_state(self, user_ip=None, user_agent=None):
        """Generate secure state with timestamp and fingerprint"""
        timestamp = int(datetime.utcnow().timestamp())
        nonce = secrets.token_urlsafe(16)
        
        # Create fingerprint from user data
        fingerprint_data = f"{user_ip or 'unknown'}:{user_agent or 'unknown'}"
        fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]
        
        # Create state data
        state_data = f"{timestamp}:{nonce}:{fingerprint}"
        
        # Generate HMAC
        signature = hmac.new(
            self.secret_key,
            state_data.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        # Combine and encode
        full_state = state_data + ':' + base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')
        return base64.urlsafe_b64encode(full_state.encode()).decode('utf-8').rstrip('=')
    
    def validate_state(self, state, user_ip=None, user_agent=None):
        """Validate state with timeout and fingerprint checking"""
        try:
            # Decode state
            decoded = base64.urlsafe_b64decode(state + '===').decode('utf-8')
            parts = decoded.split(':')
            
            if len(parts) != 4:
                logger.warning("OAuth state validation failed: Invalid format")
                return False
            
            timestamp_str, nonce, fingerprint, signature_b64 = parts
            timestamp = int(timestamp_str)
            
            # Check timeout
            if datetime.utcnow().timestamp() - timestamp > self.state_timeout:
                logger.warning("OAuth state expired")
                return False
            
            # Verify fingerprint
            expected_fingerprint = hashlib.sha256(
                f"{user_ip or 'unknown'}:{user_agent or 'unknown'}".encode()
            ).hexdigest()[:16]
            
            if fingerprint != expected_fingerprint:
                logger.warning("OAuth state fingerprint mismatch")
                return False
            
            # Verify HMAC
            state_data = f"{timestamp_str}:{nonce}:{fingerprint}"
            expected_signature = hmac.new(
                self.secret_key,
                state_data.encode('utf-8'),
                hashlib.sha256
            ).digest()
            
            provided_signature = base64.urlsafe_b64decode(signature_b64 + '===')
            
            return hmac.compare_digest(expected_signature, provided_signature)
            
        except Exception as e:
            logger.error(f"State validation error: {e}")
            return False