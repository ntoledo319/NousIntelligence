"""
Two-Factor Authentication Utilities

This module provides functions for setting up and verifying two-factor authentication.
It uses the Time-based One-Time Password (TOTP) algorithm.

@module utils.two_factor_auth
@description Two-factor authentication utilities
"""

import os
import base64
import logging
import qrcode
import pyotp
import secrets
from io import BytesIO
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash

# Configure logging
logger = logging.getLogger(__name__)

# Constants
TOTP_ISSUER = "NOUS App"
BACKUP_CODE_COUNT = 10
BACKUP_CODE_LENGTH = 10

class TOTPVerificationError(Exception):
    """Exception raised for TOTP verification errors"""
    pass

def generate_totp_secret():
    """Generate a secret key for TOTP"""
    return pyotp.random_base32()

def get_totp_uri(secret, email, issuer=TOTP_ISSUER):
    """Generate TOTP URI for QR code generation
    
    Args:
        secret: The TOTP secret key
        email: User's email for identification
        issuer: Name of the issuing application
        
    Returns:
        TOTP URI string
    """
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=issuer)

def generate_qr_code(uri):
    """Generate QR code from TOTP URI
    
    Args:
        uri: TOTP URI string
        
    Returns:
        Binary QR code image
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
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

def generate_backup_codes():
    """Generate backup codes for 2FA
    
    Returns:
        Dict with plain text codes and their hashes
    """
    codes = []
    code_hashes = []
    
    for _ in range(BACKUP_CODE_COUNT):
        # Generate random backup code
        code = ''.join(secrets.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(BACKUP_CODE_LENGTH))
        codes.append(code)
        
        # Hash the code for storage
        code_hash = generate_password_hash(code)
        code_hashes.append(code_hash)
    
    return {
        'plain_codes': codes,
        'code_hashes': code_hashes
    }

def setup_2fa_session(user_id):
    """Set up 2FA session data
    
    Args:
        user_id: ID of the user setting up 2FA
        
    Returns:
        Dict with 2FA setup data
    """
    # Generate a new secret key
    secret = generate_totp_secret()
    
    # Generate backup codes
    backup_codes_data = generate_backup_codes()
    
    # Store in session
    session['2fa_setup'] = {
        'user_id': user_id,
        'secret': secret,
        'backup_codes': backup_codes_data['code_hashes']
    }
    
    return {
        'secret': secret,
        'backup_codes': backup_codes_data['plain_codes']
    }

def confirm_2fa_setup(verification_code):
    """Confirm 2FA setup with verification code
    
    Args:
        verification_code: Code from TOTP app
        
    Returns:
        Boolean indicating success
    
    Raises:
        TOTPVerificationError: If verification fails
    """
    # Check if setup is in progress
    if '2fa_setup' not in session:
        raise TOTPVerificationError("No 2FA setup in progress")
    
    # Get secret from session
    setup_data = session.get('2fa_setup')
    secret = setup_data.get('secret')
    
    if not secret:
        raise TOTPVerificationError("No secret found in session")
    
    # Verify the code
    if not verify_totp(secret, verification_code):
        raise TOTPVerificationError("Invalid verification code")
    
    # Return success
    return True

def verify_totp(secret, verification_code):
    """Verify a TOTP code
    
    Args:
        secret: TOTP secret key
        verification_code: Code from TOTP app
        
    Returns:
        Boolean indicating success
    """
    try:
        # Create TOTP instance
        totp = pyotp.TOTP(secret)
        
        # Verify with 30-second window on either side
        return totp.verify(verification_code, valid_window=1)
    except Exception as e:
        logger.error(f"TOTP verification error: {str(e)}")
        return False

def verify_backup_code(provided_code, stored_code_hash):
    """Verify a backup code
    
    Args:
        provided_code: Code provided by user
        stored_code_hash: Stored hash of the backup code
        
    Returns:
        Boolean indicating success
    """
    try:
        return check_password_hash(stored_code_hash, provided_code)
    except Exception as e:
        logger.error(f"Backup code verification error: {str(e)}")
        return False 