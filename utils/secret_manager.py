"""
Secret Management Module

Provides secure secret generation and validation for the application.
Implements best practices for cryptographic secret handling.
"""

import secrets
import hashlib
import base64
from typing import Tuple, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class SecretManager:
    """Manages cryptographic secrets and keys for the application"""
    
    @staticmethod
    def generate_secure_secret(length: int = 64) -> str:
        """
        Generate a cryptographically secure random secret.
        
        Args:
            length: Length of the secret (default: 64 characters)
            
        Returns:
            str: URL-safe base64 encoded secret
        """
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_hex_secret(length: int = 32) -> str:
        """
        Generate a hex-encoded secret.
        
        Args:
            length: Number of bytes (resulting string will be 2x length)
            
        Returns:
            str: Hex-encoded secret
        """
        return secrets.token_hex(length)
    
    @staticmethod
    def validate_secret_strength(secret: str) -> Tuple[bool, str]:
        """
        Validate that a secret meets security requirements.
        
        Args:
            secret: The secret to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, message)
        """
        if not secret:
            return False, "Secret cannot be empty"
            
        if len(secret) < 64:
            return False, "Secret must be at least 64 characters long"
            
        # Check entropy by counting unique characters
        unique_chars = len(set(secret))
        if unique_chars < 20:
            return False, "Secret has insufficient entropy (too few unique characters)"
            
        # Check for common weak patterns
        weak_patterns = ['1234', 'abcd', '0000', 'password', 'secret']
        secret_lower = secret.lower()
        for pattern in weak_patterns:
            if pattern in secret_lower:
                return False, f"Secret contains weak pattern: {pattern}"
                
        return True, "Secret meets security requirements"
    
    @staticmethod
    def derive_key_from_secret(secret: str, salt: bytes = b'nous-app-salt') -> bytes:
        """
        Derive an encryption key from a secret using PBKDF2.
        
        Args:
            secret: The secret to derive from
            salt: Salt for key derivation (should be unique per use case)
            
        Returns:
            bytes: 32-byte encryption key
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret.encode()))
        return key
    
    @staticmethod
    def create_fernet_key() -> bytes:
        """
        Create a new Fernet encryption key.
        
        Returns:
            bytes: Fernet key
        """
        return Fernet.generate_key()
    
    @staticmethod
    def hash_secret(secret: str, salt: Optional[str] = None) -> str:
        """
        Create a secure hash of a secret.
        
        Args:
            secret: The secret to hash
            salt: Optional salt (will be generated if not provided)
            
        Returns:
            str: Salt and hash in format "salt$hash"
        """
        if salt is None:
            salt = secrets.token_hex(16)
            
        # Use PBKDF2 for secure hashing
        dk = hashlib.pbkdf2_hmac(
            'sha256',
            secret.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # iterations
        )
        
        return f"{salt}${dk.hex()}"
    
    @staticmethod
    def verify_secret_hash(secret: str, hashed: str) -> bool:
        """
        Verify a secret against its hash.
        
        Args:
            secret: The secret to verify
            hashed: The salt$hash string
            
        Returns:
            bool: True if the secret matches
        """
        try:
            salt, hash_hex = hashed.split('$', 1)
            new_hash = SecretManager.hash_secret(secret, salt)
            return secrets.compare_digest(new_hash, hashed)
        except (ValueError, AttributeError):
            return False
    
    @staticmethod
    def generate_api_key() -> str:
        """
        Generate a secure API key.
        
        Returns:
            str: API key in format "nous_XXXXX"
        """
        prefix = "nous"
        key = secrets.token_urlsafe(32)
        return f"{prefix}_{key}"
    
    @staticmethod
    def generate_session_secret() -> str:
        """
        Generate a secure session secret.
        
        Returns:
            str: Session secret suitable for Flask
        """
        return SecretManager.generate_secure_secret(64)
    
    @staticmethod
    def rotate_secret(old_secret: str, new_secret: str, data_to_reencrypt: list) -> list:
        """
        Rotate encryption by re-encrypting data with a new secret.
        
        Args:
            old_secret: The current secret
            new_secret: The new secret to use
            data_to_reencrypt: List of encrypted data items
            
        Returns:
            list: Re-encrypted data items
        """
        # Derive keys from secrets
        old_key = SecretManager.derive_key_from_secret(old_secret)
        new_key = SecretManager.derive_key_from_secret(new_secret)
        
        # Create Fernet instances
        old_fernet = Fernet(old_key)
        new_fernet = Fernet(new_key)
        
        # Re-encrypt each item
        reencrypted = []
        for item in data_to_reencrypt:
            try:
                # Decrypt with old key
                plaintext = old_fernet.decrypt(item.encode())
                # Encrypt with new key
                new_ciphertext = new_fernet.encrypt(plaintext)
                reencrypted.append(new_ciphertext.decode())
            except Exception:
                # If decryption fails, skip this item
                continue
                
        return reencrypted


# Convenience functions
def generate_secure_secret(length: int = 64) -> str:
    """Generate a secure secret."""
    return SecretManager.generate_secure_secret(length)


def validate_secret(secret: str) -> Tuple[bool, str]:
    """Validate a secret's strength."""
    return SecretManager.validate_secret_strength(secret)


def generate_api_key() -> str:
    """Generate an API key."""
    return SecretManager.generate_api_key()


def validate_all_secrets() -> dict:
    """
    Validate all critical secrets used by the application.
    
    Returns:
        Dictionary with validation results for each secret
    """
    results = {}
    
    # List of critical environment variables to validate
    critical_secrets = [
        'SESSION_SECRET',
        'GOOGLE_CLIENT_SECRET',
        'DATABASE_URL'
    ]
    
    for secret_name in critical_secrets:
        is_valid, message = SecretManager.validate_environment_secret(secret_name)
        results[secret_name] = {
            'valid': is_valid,
            'message': message
        }
    
    return results


if __name__ == "__main__":
    # Test secret validation
    test_secret = SecretManager.generate_secure_secret()
    is_valid, message = SecretManager.validate_secret_strength(test_secret)
    print(f"Generated secret validation: {is_valid} - {message}")
    
    # Validate all environment secrets
    results = validate_all_secrets()
    print("\nEnvironment Secret Validation:")
    for secret, result in results.items():
        status = "✅" if result['valid'] else "❌"
        print(f"{status} {secret}: {result['message']}")