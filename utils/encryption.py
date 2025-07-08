import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class FieldEncryption:
    def __init__(self):
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)
    
    def _get_or_create_key(self):
        """Get encryption key from environment or generate one"""
        key_str = os.getenv('ENCRYPTION_KEY')
        if key_str:
            return key_str.encode()
        
        # Generate key from password if available
        password = os.getenv('SECRET_KEY', 'default-key').encode()
        salt = b'salt_'  # In production, use proper random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        if not data:
            return data
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, data: str) -> str:
        """Decrypt sensitive data"""
        if not data:
            return data
        try:
            return self.cipher.decrypt(data.encode()).decode()
        except:
            return data  # Return as-is if decryption fails (migration)

# Global instance
encryptor = FieldEncryption()

def encrypt_field(data):
    """Helper function to encrypt a field"""
    return encryptor.encrypt(str(data)) if data else None

def decrypt_field(data):
    """Helper function to decrypt a field"""
    return encryptor.decrypt(str(data)) if data else None
