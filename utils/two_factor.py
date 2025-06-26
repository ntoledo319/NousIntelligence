"""
Two-Factor Authentication Module

This module provides utilities for implementing two-factor authentication
using the TOTP (Time-based One-Time Password) standard.

@module two_factor
@description Two-factor authentication utilities
"""

import os
import base64
import logging
import pyotp
import qrcode
from io import BytesIO
from datetime import datetime, timedelta
from flask import current_app, session, url_for
from typing import Tuple, Optional

# Configure logging
logger = logging.getLogger(__name__)

def generate_totp_secret() -> str:
    """
    Generate a new random secret key for TOTP

    Returns:
        str: Base32-encoded secret key
    """
    return pyotp.random_base32()

def create_totp_uri(secret: str, email: str) -> str:
    """
    Create a TOTP URI for QR code generation

    Args:
        secret: TOTP secret key
        email: User's email address

    Returns:
        str: TOTP URI for QR code
    """
    app_name = current_app.config.get('APP_NAME', 'NOUS Assistant')
    return pyotp.totp.TOTP(secret).provisioning_uri(
        name=email,
        issuer_name=app_name
    )

def generate_qr_code(uri: str) -> str:
    """
    Generate a QR code image as a data URL

    Args:
        uri: TOTP URI

    Returns:
        str: Data URL of QR code image
    """
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to data URL
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')

        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        logger.error(f"Error generating QR code: {str(e)}")
        return ""

def verify_totp(secret: str, token: str) -> bool:
    """
    Verify a TOTP token

    Args:
        secret: TOTP secret key
        token: User-provided token

    Returns:
        bool: True if token is valid
    """
    if not secret or not token:
        return False

    try:
        totp = pyotp.TOTP(secret)
        return totp.verify(token)
    except Exception as e:
        logger.error(f"Error verifying TOTP: {str(e)}")
        return False

def generate_backup_codes(count: int = 10) -> list:
    """
    Generate backup codes for 2FA recovery

    Args:
        count: Number of backup codes to generate

    Returns:
        list: List of backup codes
    """
    codes = []
    for _ in range(count):
        # Generate an 8-character code
        code = pyotp.random_base32(8).lower()
        # Format as XXXX-XXXX
        code = f"{code[:4]}-{code[4:]}"
        codes.append(code)
    return codes

def verify_backup_code(user_id: str, code: str) -> bool:
    """
    Verify a backup code

    Args:
        user_id: User ID
        code: Backup code to verify

    Returns:
        bool: True if code is valid and unused
    """
    from models import TwoFactorBackupCode, db

    # Normalize the code format
    code = code.strip().replace("-", "").upper()

    try:
        # Find the backup code
        backup_code = TwoFactorBackupCode.query.filter_by(
            user_id=user_id,
            used=False
        ).filter(
            TwoFactorBackupCode.code.ilike(f"{code[:4]}%{code[4:]}")
        ).first()

        if not backup_code:
            return False

        # Mark code as used
        backup_code.used = True
        backup_code.used_at = datetime.utcnow()
        db.session.commit()

        return True
    except Exception as e:
        logger.error(f"Error verifying backup code: {str(e)}")
        db.session.rollback()
        return False

def setup_2fa_session(user_id: str) -> None:
    """
    Set up a session for 2FA verification

    This creates a temporary session that remembers the user is partially authenticated
    and needs to complete 2FA verification.

    Args:
        user_id: User ID
    """
    session['2fa_user_id'] = user_id
    session['2fa_required'] = True
    session['2fa_timestamp'] = datetime.utcnow().timestamp()
    # Set a short timeout for 2FA verification
    session['2fa_timeout'] = (datetime.utcnow() + timedelta(minutes=5)).timestamp()

def clear_2fa_session() -> None:
    """Clear 2FA session data"""
    session.pop('2fa_user_id', None)
    session.pop('2fa_required', None)
    session.pop('2fa_timestamp', None)
    session.pop('2fa_timeout', None)

def is_2fa_session_valid() -> bool:
    """
    Check if the current 2FA session is valid

    Returns:
        bool: True if session is valid
    """
    if '2fa_required' not in session or '2fa_timeout' not in session:
        return False

    # Check if the session has expired
    timeout = session.get('2fa_timeout', 0)
    if timeout < datetime.utcnow().timestamp():
        clear_2fa_session()
        return False

    return True

def is_trusted_device(user_id: str) -> bool:
    """
    Check if the current device is a trusted device for the user

    Args:
        user_id: User ID

    Returns:
        bool: True if device is trusted
    """
    device_id = session.get('device_id')

    if not device_id:
        return False

    # Check if device ID exists in database
    from models import TrustedDevice

    try:
        device = TrustedDevice.query.filter_by(
            user_id=user_id,
            device_id=device_id,
            is_trusted=True
        ).first()

        return device is not None
    except Exception as e:
        logger.error(f"Error checking trusted device: {str(e)}")
        return False

def add_trusted_device(user_id: str, device_name: str) -> bool:
    """
    Add the current device as a trusted device

    Args:
        user_id: User ID
        device_name: User-friendly device name

    Returns:
        bool: True if device was added successfully
    """
    from models import TrustedDevice, db

    # Generate a unique device ID if not already set
    if 'device_id' not in session:
        session['device_id'] = os.urandom(32).hex()

    device_id = session['device_id']

    try:
        # Check if device already exists
        device = TrustedDevice.query.filter_by(
            user_id=user_id,
            device_id=device_id
        ).first()

        if device:
            # Update existing device
            device.is_trusted = True
            device.name = device_name
            device.last_used = datetime.utcnow()
        else:
            # Create new device
            device = TrustedDevice(
                user_id=user_id,
                device_id=device_id,
                name=device_name,
                is_trusted=True
            )
            db.session.add(device)

        db.session.commit()
        return True
    except Exception as e:
        logger.error(f"Error adding trusted device: {str(e)}")
        db.session.rollback()
        return False