"""
Two-Factor Authentication Module

This module provides functionality for implementing two-factor authentication (2FA)
using Time-based One-Time Passwords (TOTP) compatible with Google Authenticator
and similar apps.

@module: two_factor_auth
@author: NOUS Development Team
"""
import os
import base64
import hmac
import time
import hashlib
import logging
import qrcode
import io
import random
import string
from typing import Tuple, Optional, Dict, List
from urllib.parse import quote
from flask import current_app, request, session

# Configure logger
logger = logging.getLogger(__name__)

# TOTP Constants
TOTP_DIGITS = 6
TOTP_INTERVAL = 30  # seconds
TOTP_ISSUER = os.environ.get('TOTP_ISSUER', 'NOUS')

# Backup codes constants
BACKUP_CODE_COUNT = 10
BACKUP_CODE_LENGTH = 8

class TOTPVerificationError(Exception):
    """Exception raised when TOTP verification fails"""
    pass

def generate_totp_secret() -> str:
    """
    Generate a random secret key for TOTP
    
    Returns:
        Base32 encoded secret key
    """
    # Generate 20 random bytes (160 bits)
    random_bytes = os.urandom(20)
    
    # Convert to base32 for easier manual entry
    secret = base64.b32encode(random_bytes).decode('utf-8')
    
    return secret

def generate_totp(secret: str, timestamp: Optional[int] = None) -> str:
    """
    Generate a TOTP code for a given secret
    
    Args:
        secret: Base32 encoded secret key
        timestamp: Optional timestamp (current time if None)
        
    Returns:
        TOTP code as string
    """
    if timestamp is None:
        timestamp = int(time.time())
    
    # Calculate time step from timestamp
    time_step = timestamp // TOTP_INTERVAL
    
    # Decode the base32 secret
    secret_bytes = base64.b32decode(secret.upper())
    
    # Convert time step to bytes (8 bytes, big endian)
    time_bytes = time_step.to_bytes(8, byteorder='big')
    
    # Generate HMAC-SHA1
    hmac_hash = hmac.new(secret_bytes, time_bytes, hashlib.sha1).digest()
    
    # Dynamic truncation
    offset = hmac_hash[-1] & 0x0F
    binary = ((hmac_hash[offset] & 0x7F) << 24 |
              (hmac_hash[offset + 1] & 0xFF) << 16 |
              (hmac_hash[offset + 2] & 0xFF) << 8 |
              (hmac_hash[offset + 3] & 0xFF))
    
    # Generate OTP
    otp = binary % (10 ** TOTP_DIGITS)
    
    # Ensure it's the correct length by zero-padding
    return str(otp).zfill(TOTP_DIGITS)

def verify_totp(secret: str, code: str, window: int = 1) -> bool:
    """
    Verify a TOTP code against a secret
    
    Args:
        secret: Base32 encoded secret key
        code: TOTP code to verify
        window: Time window to allow codes from (in intervals)
        
    Returns:
        True if valid, False otherwise
    """
    if not code or not secret:
        return False
    
    # Try to normalize the code
    try:
        code = code.strip()
        if not code.isdigit():
            return False
    except (AttributeError, ValueError):
        return False
    
    # Check for current time and surrounding intervals
    now = int(time.time())
    for i in range(-window, window + 1):
        timestamp = now + (i * TOTP_INTERVAL)
        if generate_totp(secret, timestamp) == code:
            return True
    
    return False

def get_totp_uri(secret: str, account_name: str) -> str:
    """
    Generate a TOTP URI for QR code generation
    
    Args:
        secret: Base32 encoded secret key
        account_name: User's account name or email
        
    Returns:
        otpauth URI string
    """
    issuer = quote(TOTP_ISSUER)
    account = quote(account_name)
    
    return (f"otpauth://totp/{issuer}:{account}?"
            f"secret={secret}&issuer={issuer}&"
            f"algorithm=SHA1&digits={TOTP_DIGITS}&period={TOTP_INTERVAL}")

def generate_qr_code(uri: str) -> bytes:
    """
    Generate a QR code image for a TOTP URI
    
    Args:
        uri: TOTP URI to encode in QR code
        
    Returns:
        QR code image as bytes
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert PIL image to bytes
    img_byte_array = io.BytesIO()
    img.save(img_byte_array, format='PNG')
    
    return img_byte_array.getvalue()

def generate_backup_codes() -> List[str]:
    """
    Generate backup codes for 2FA recovery
    
    Returns:
        List of backup codes
    """
    codes = []
    for _ in range(BACKUP_CODE_COUNT):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=BACKUP_CODE_LENGTH))
        codes.append(code)
    
    return codes

def hash_backup_code(code: str) -> str:
    """
    Hash a backup code for storage
    
    Args:
        code: Backup code to hash
        
    Returns:
        Hashed backup code
    """
    salt = os.urandom(16)
    hash_obj = hashlib.pbkdf2_hmac('sha256', code.encode(), salt, 100000)
    
    # Store salt and hash together
    return base64.b64encode(salt + hash_obj).decode('utf-8')

def verify_backup_code(code: str, stored_hash: str) -> bool:
    """
    Verify a backup code against its stored hash
    
    Args:
        code: Backup code to verify
        stored_hash: Previously stored hash
        
    Returns:
        True if valid, False otherwise
    """
    try:
        # Decode the stored hash
        hash_data = base64.b64decode(stored_hash.encode('utf-8'))
        
        # Extract salt (first 16 bytes) and hash
        salt = hash_data[:16]
        stored_hash_value = hash_data[16:]
        
        # Hash the provided code with the same salt
        hash_obj = hashlib.pbkdf2_hmac('sha256', code.encode(), salt, 100000)
        
        # Compare in constant time
        return hmac.compare_digest(stored_hash_value, hash_obj)
    except Exception as e:
        logger.error(f"Error verifying backup code: {str(e)}")
        return False

def setup_2fa_session(user_id: int) -> Dict:
    """
    Set up a new 2FA enrollment session
    
    Args:
        user_id: User ID
        
    Returns:
        Dict with 2FA enrollment data
    """
    # Generate new TOTP secret
    secret = generate_totp_secret()
    
    # Generate backup codes
    backup_codes = generate_backup_codes()
    
    # Hash backup codes for storage
    hashed_backup_codes = [hash_backup_code(code) for code in backup_codes]
    
    # Store in session temporarily (will be moved to database after verification)
    session['2fa_setup'] = {
        'user_id': user_id,
        'secret': secret,
        'backup_codes': hashed_backup_codes,
        'setup_time': int(time.time())
    }
    
    return {
        'secret': secret,
        'backup_codes': backup_codes
    }

def confirm_2fa_setup(code: str) -> bool:
    """
    Confirm 2FA setup with a verification code
    
    Args:
        code: TOTP code from authenticator app
        
    Returns:
        True if confirmed successfully
    """
    # Check if we have 2FA setup in session
    if '2fa_setup' not in session:
        raise TOTPVerificationError("No 2FA setup in progress")
    
    setup_data = session['2fa_setup']
    secret = setup_data['secret']
    
    # Verify the code
    if not verify_totp(secret, code):
        raise TOTPVerificationError("Invalid verification code")
    
    # At this point, the code is verified and the setup is confirmed
    # The caller should now save the 2FA data to the database
    
    return True

def require_2fa(f):
    """
    Decorator to require 2FA verification for a route
    
    This decorator should be applied after authentication to ensure
    the user has completed 2FA verification for this session.
    """
    from functools import wraps
    
    @wraps(f)
    def decorated(*args, **kwargs):
        from flask import redirect, url_for
        
        # Check if user is logged in
        if not hasattr(request, 'user') or not request.user:
            return redirect(url_for('login'))
        
        # Check if 2FA is enabled for this user
        if not request.user.two_factor_enabled:
            # 2FA not enabled for this user, proceed
            return f(*args, **kwargs)
        
        # Check if 2FA is verified for this session
        if not session.get('2fa_verified'):
            # Not verified, redirect to 2FA verification page
            session['after_2fa_url'] = request.url
            return redirect(url_for('auth.verify_2fa'))
        
        # 2FA verified, proceed
        return f(*args, **kwargs)
    
    return decorated 