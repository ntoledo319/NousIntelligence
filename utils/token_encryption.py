"""
Token Encryption Module
Provides secure encryption for OAuth tokens using Fernet symmetric encryption
"""

import os
import base64
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)

class TokenEncryption:
    """Handles encryption/decryption of sensitive tokens"""
    
    def __init__(self, master_key=None):
        if master_key:
            self.cipher = Fernet(master_key)
        else:
            # Derive key from environment variable
            secret = os.environ.get('TOKEN_ENCRYPTION_KEY', os.environ.get('SESSION_SECRET', ''))
            if not secret:
                raise ValueError("TOKEN_ENCRYPTION_KEY or SESSION_SECRET required for token encryption")
            
            # Use PBKDF2 to derive a proper key from the secret
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'nous-oauth-tokens',  # Static salt for deterministic key
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(secret.encode()))
            self.cipher = Fernet(key)
    
    def encrypt_token(self, token):
        """Encrypt a token string"""
        if not token:
            return None
        
        try:
            return self.cipher.encrypt(token.encode()).decode()
        except Exception as e:
            logger.error(f"Token encryption failed: {e}")
            raise
    
    def decrypt_token(self, encrypted_token):
        """Decrypt a token string"""
        if not encrypted_token:
            return None
        
        try:
            return self.cipher.decrypt(encrypted_token.encode()).decode()
        except Exception as e:
            logger.error(f"Token decryption failed: {e}")
            return None  # Return None for invalid tokens instead of raising

# Global instance
try:
    token_encryption = TokenEncryption()
except (ValueError, ImportError) as e:
    logger.warning(f"Token encryption not available: {e}")
    token_encryption = None