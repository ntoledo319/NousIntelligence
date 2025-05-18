"""
Environment Variable Loader

This module loads environment variables from a .env file if present.
It should be imported before any other application components to ensure
environment variables are available from startup.
"""

import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def load_dotenv(envfile=".env"):
    """
    Load environment variables from a .env file
    
    Args:
        envfile: Path to .env file (default: .env in current directory)
        
    Returns:
        bool: True if .env file was loaded, False otherwise
    """
    envpath = Path(envfile)
    
    if not envpath.exists():
        return False
    
    with open(envpath) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            # Strip quotes if present
            if value and value[0] == value[-1] in ['"', "'"]:
                value = value[1:-1]
                
            # Only set if not already in environment
            if key not in os.environ:
                os.environ[key] = value
    
    return True

def ensure_secret_key():
    """
    Ensure a SECRET_KEY is set in the environment
    
    If SECRET_KEY is not set, but SESSION_SECRET is, copy it over.
    If neither are set, generate a new one.
    """
    if os.environ.get("SECRET_KEY"):
        # Already set, nothing to do
        return
    
    # Check for SESSION_SECRET as fallback
    if os.environ.get("SESSION_SECRET"):
        os.environ["SECRET_KEY"] = os.environ["SESSION_SECRET"]
        return
    
    # Generate a new secret key if needed
    import binascii
    secret_key = binascii.hexlify(os.urandom(24)).decode()
    os.environ["SECRET_KEY"] = secret_key
    
    # Write to .secret_key file for persistence
    try:
        with open(".secret_key", "w") as f:
            f.write(secret_key)
        
        # Update .env file if it exists
        if os.path.exists(".env"):
            with open(".env", "a") as f:
                f.write(f"\nSECRET_KEY={secret_key}\n")
    except Exception as e:
        logger.warning(f"Could not save generated SECRET_KEY: {str(e)}")

# Load environment variables from .env file
loaded = load_dotenv()
if loaded:
    logger.info("Loaded environment variables from .env file")

# Ensure SECRET_KEY is set
ensure_secret_key()