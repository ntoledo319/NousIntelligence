"""
Secret Management Utility
Provides secure secret generation and validation for NOUS application
"""
import secrets
import os
from typing import Tuple


class SecretManager:
    """Manages secure secrets and validates their strength"""
    
    @staticmethod
    def generate_secure_secret(length: int = 64) -> str:
        """
        Generate a cryptographically secure secret.
        
        Args:
            length: Length of the secret to generate (default: 64)
            
        Returns:
            URL-safe base64 encoded secret string
        """
        return secrets.token_urlsafe(length)

    @staticmethod
    def validate_secret_strength(secret: str) -> Tuple[bool, str]:
        """
        Validate the strength of a secret.
        
        Args:
            secret: The secret string to validate
            
        Returns:
            Tuple of (is_valid: bool, message: str)
        """
        if not secret:
            return False, "Secret is empty"
            
        if len(secret) < 64:
            return False, "Secret too short (<64 chars)"
            
        if len(set(secret)) < 20:
            return False, "Low entropy - secret lacks character diversity"
            
        # Check for common patterns
        if secret.lower() in ['password', 'secret', 'key']:
            return False, "Secret contains common words"
            
        return True, "Secret is strong"
    
    @staticmethod
    def validate_environment_secret(env_var_name: str) -> Tuple[bool, str]:
        """
        Validate a secret from environment variables.
        
        Args:
            env_var_name: Name of the environment variable
            
        Returns:
            Tuple of (is_valid: bool, message: str)
        """
        secret = os.getenv(env_var_name, "")
        if not secret:
            return False, f"Environment variable {env_var_name} is not set"
        
        return SecretManager.validate_secret_strength(secret)
    
    @staticmethod
    def get_validated_secret(env_var_name: str, min_length: int = 64) -> str:
        """
        Get and validate a secret from environment variables.
        
        Args:
            env_var_name: Name of the environment variable
            min_length: Minimum required length
            
        Returns:
            The validated secret
            
        Raises:
            RuntimeError: If secret is invalid or missing
        """
        secret = os.getenv(env_var_name, "")
        if not secret:
            raise RuntimeError(f"Missing required environment variable: {env_var_name}")
        
        if len(secret) < min_length:
            raise RuntimeError(f"Environment variable {env_var_name} must be at least {min_length} characters")
        
        is_valid, message = SecretManager.validate_secret_strength(secret)
        if not is_valid:
            raise RuntimeError(f"Weak {env_var_name}: {message}")
        
        return secret


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