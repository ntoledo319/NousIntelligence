"""
Two-Factor Authentication Routes

This module provides routes for setting up and using two-factor authentication.

@module auth.two_factor
@description Two-factor authentication routes
"""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash
import json

from utils.two_factor import (
    generate_totp_secret, create_totp_uri, generate_qr_code, verify_totp,
    generate_backup_codes, setup_2fa_session, clear_2fa_session, is_2fa_session_valid,
    is_trusted_device, add_trusted_device
)
from models import db, User
from utils.security import log_security_event, generate_csrf_token

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
two_factor_bp = Blueprint('two_factor', __name__, url_prefix='/auth/2fa')

@two_factor_bp.route('/setup', methods=['GET', 'POST'])
@login_required
def setup():
    """Set up two-factor authentication"""
    if request.method == 'GET':
        # Generate a new secret key
        secret = generate_totp_secret()
        
        # Create TOTP URI for QR code
        totp_uri = create_totp_uri(secret, current_user.email)
        
        # Generate QR code
        qr_code = generate_qr_code(totp_uri)
        
        # Store secret in session temporarily
        session['totp_setup_secret'] = secret
        
        # Generate CSRF token
        csrf_token = generate_csrf_token()
        
        return render_template(
            'auth/2fa_setup.html',
            secret=secret,
            qr_code=qr_code,
            csrf_token=csrf_token
        )
    
    elif request.method == 'POST':
        # Verify CSRF token
        if not session.get('csrf_token') or session.get('csrf_token') != request.form.get('csrf_token'):
            flash('Invalid request. Please try again.', 'danger')
            return redirect(url_for('two_factor.setup'))
        
        # Get the token from form
        token = request.form.get('token', '')
        
        # Get the secret from session
        secret = session.get('totp_setup_secret', '')
        
        if not secret:
            flash('Setup session expired. Please try again.', 'danger')
            return redirect(url_for('two_factor.setup'))
        
        # Verify the token
        if not verify_totp(secret, token):
            flash('Invalid verification code. Please try again.', 'danger')
            return redirect(url_for('two_factor.setup'))
        
        # Setup 2FA in the database
        try:
            # Update user model
            if current_user.two_factor_auth:
                # Update existing 2FA settings
                current_user.two_factor_auth.secret_key = secret
                current_user.two_factor_auth.enabled = True
                current_user.two_factor_auth.verified = True
            else:
                # Setup 2FA for the first time
                from models.security_models import TwoFactorAuth
                
                tfa = TwoFactorAuth(
                    user_id=current_user.id,
                    secret_key=secret,
                    enabled=True,
                    verified=True
                )
                db.session.add(tfa)
            
            # Update user profile
            current_user.requires_2fa = True
            
            # Generate backup codes
            backup_codes = current_user.generate_backup_codes()
            
            # Clear the secret from session
            session.pop('totp_setup_secret', None)
            
            # Commit changes
            db.session.commit()
            
            # Log the event
            log_security_event(
                'two_factor_enabled', 
                current_user.id, 
                f"Two-factor authentication enabled for {current_user.email}",
                request.remote_addr
            )
            
            flash('Two-factor authentication has been enabled successfully.', 'success')
            
            # Show backup codes
            return render_template(
                'auth/2fa_backup_codes.html',
                backup_codes=backup_codes
            )
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error enabling 2FA: {str(e)}")
            flash('An error occurred. Please try again.', 'danger')
            return redirect(url_for('two_factor.setup'))

@two_factor_bp.route('/verify', methods=['GET', 'POST'])
def verify():
    """Verify 2FA code during login"""
    if not is_2fa_session_valid():
        flash('Authentication session expired. Please login again.', 'danger')
        return redirect(url_for('auth.login'))
    
    # Get user ID from session
    user_id = session.get('2fa_user_id')
    
    # Get user
    user = User.query.get(user_id)
    if not user or not user.requires_2fa:
        clear_2fa_session()
        flash('Invalid authentication session. Please login again.', 'danger')
        return redirect(url_for('auth.login'))
    
    # Check if device is already trusted
    if is_trusted_device(user.id):
        # Complete login
        from flask_login import login_user
        login_user(user)
        
        # Clear 2FA session
        clear_2fa_session()
        
        # Log the event
        log_security_event(
            'login_success_trusted_device', 
            user.id, 
            f"Login successful with trusted device for {user.email}",
            request.remote_addr,
            metadata=json.dumps({
                'user_agent': request.user_agent.string
            })
        )
        
        flash('Login successful! Welcome back.', 'success')
        return redirect(url_for('index'))
    
    if request.method == 'GET':
        # Generate CSRF token
        csrf_token = generate_csrf_token()
        
        return render_template(
            'auth/2fa_verify.html',
            csrf_token=csrf_token,
            user_email=user.email
        )
    
    elif request.method == 'POST':
        # Verify CSRF token
        if not session.get('csrf_token') or session.get('csrf_token') != request.form.get('csrf_token'):
            flash('Invalid request. Please try again.', 'danger')
            return redirect(url_for('two_factor.verify'))
        
        # Get the token from form
        token = request.form.get('token', '')
        
        # Check if using backup code
        is_backup = request.form.get('use_backup') == '1'
        
        # Get the remember option
        remember_device = request.form.get('remember_device') == '1'
        
        if is_backup:
            # Verify backup code
            from utils.two_factor import verify_backup_code
            
            if not verify_backup_code(user.id, token):
                flash('Invalid backup code. Please try again.', 'danger')
                
                # Log the event
                log_security_event(
                    'two_factor_failed', 
                    user.id, 
                    f"Invalid backup code for {user.email}",
                    request.remote_addr,
                    severity='WARNING'
                )
                
                return redirect(url_for('two_factor.verify'))
        else:
            # Get user's 2FA secret
            if not user.two_factor_auth or not user.two_factor_auth.secret_key:
                flash('Two-factor authentication is not properly set up. Please contact support.', 'danger')
                clear_2fa_session()
                return redirect(url_for('auth.login'))
            
            # Verify the token
            if not verify_totp(user.two_factor_auth.secret_key, token):
                flash('Invalid verification code. Please try again.', 'danger')
                
                # Log the event
                log_security_event(
                    'two_factor_failed', 
                    user.id, 
                    f"Invalid 2FA code for {user.email}",
                    request.remote_addr,
                    severity='WARNING'
                )
                
                return redirect(url_for('two_factor.verify'))
        
        # If we get here, 2FA verification was successful
        from flask_login import login_user
        login_user(user)
        
        # Clear 2FA session
        clear_2fa_session()
        
        # Remember device if requested
        if remember_device:
            device_name = request.user_agent.browser
            add_trusted_device(user.id, device_name)
            
            # Log the event
            log_security_event(
                'trusted_device_added', 
                user.id, 
                f"Trusted device added for {user.email}: {device_name}",
                request.remote_addr
            )
        
        # Log the event
        log_security_event(
            'login_success_2fa', 
            user.id, 
            f"Login successful with 2FA for {user.email}",
            request.remote_addr
        )
        
        flash('Login successful! Welcome back.', 'success')
        return redirect(url_for('index'))

@two_factor_bp.route('/disable', methods=['GET', 'POST'])
@login_required
def disable():
    """Disable two-factor authentication"""
    if request.method == 'GET':
        # Generate CSRF token
        csrf_token = generate_csrf_token()
        
        return render_template(
            'auth/2fa_disable.html',
            csrf_token=csrf_token
        )
    
    elif request.method == 'POST':
        # Verify CSRF token
        if not session.get('csrf_token') or session.get('csrf_token') != request.form.get('csrf_token'):
            flash('Invalid request. Please try again.', 'danger')
            return redirect(url_for('two_factor.disable'))
        
        # Get the password from form
        password = request.form.get('password', '')
        
        # Verify the password
        if not check_password_hash(current_user.password_hash, password):
            flash('Invalid password. Please try again.', 'danger')
            
            # Log the event
            log_security_event(
                'two_factor_disable_failed', 
                current_user.id, 
                f"Failed 2FA disable attempt for {current_user.email} (invalid password)",
                request.remote_addr,
                severity='WARNING'
            )
            
            return redirect(url_for('two_factor.disable'))
        
        # Disable 2FA
        try:
            current_user.disable_2fa()
            db.session.commit()
            
            # Log the event
            log_security_event(
                'two_factor_disabled', 
                current_user.id, 
                f"Two-factor authentication disabled for {current_user.email}",
                request.remote_addr
            )
            
            flash('Two-factor authentication has been disabled successfully.', 'success')
            return redirect(url_for('profile.security'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error disabling 2FA: {str(e)}")
            flash('An error occurred. Please try again.', 'danger')
            return redirect(url_for('two_factor.disable'))

@two_factor_bp.route('/backup-codes', methods=['GET', 'POST'])
@login_required
def backup_codes():
    """Generate new backup codes"""
    if not current_user.requires_2fa:
        flash('You need to enable two-factor authentication first.', 'warning')
        return redirect(url_for('two_factor.setup'))
    
    if request.method == 'GET':
        # Generate CSRF token
        csrf_token = generate_csrf_token()
        
        return render_template(
            'auth/2fa_regenerate_codes.html',
            csrf_token=csrf_token
        )
    
    elif request.method == 'POST':
        # Verify CSRF token
        if not session.get('csrf_token') or session.get('csrf_token') != request.form.get('csrf_token'):
            flash('Invalid request. Please try again.', 'danger')
            return redirect(url_for('two_factor.backup_codes'))
        
        # Get the password from form
        password = request.form.get('password', '')
        
        # Verify the password
        if not check_password_hash(current_user.password_hash, password):
            flash('Invalid password. Please try again.', 'danger')
            
            # Log the event
            log_security_event(
                'backup_codes_regenerate_failed', 
                current_user.id, 
                f"Failed backup codes regeneration attempt for {current_user.email} (invalid password)",
                request.remote_addr,
                severity='WARNING'
            )
            
            return redirect(url_for('two_factor.backup_codes'))
        
        # Generate new backup codes
        try:
            backup_codes = current_user.generate_backup_codes()
            db.session.commit()
            
            # Log the event
            log_security_event(
                'backup_codes_regenerated', 
                current_user.id, 
                f"Backup codes regenerated for {current_user.email}",
                request.remote_addr
            )
            
            return render_template(
                'auth/2fa_backup_codes.html',
                backup_codes=backup_codes
            )
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error generating backup codes: {str(e)}")
            flash('An error occurred. Please try again.', 'danger')
            return redirect(url_for('two_factor.backup_codes'))

@two_factor_bp.route('/trusted-devices', methods=['GET'])
@login_required
def trusted_devices():
    """Manage trusted devices"""
    if not current_user.requires_2fa:
        flash('You need to enable two-factor authentication first.', 'warning')
        return redirect(url_for('two_factor.setup'))
    
    # Get trusted devices
    from models.security_models import TrustedDevice
    
    devices = TrustedDevice.query.filter_by(
        user_id=current_user.id,
        is_trusted=True
    ).order_by(TrustedDevice.last_used.desc()).all()
    
    # Generate CSRF token
    csrf_token = generate_csrf_token()
    
    return render_template(
        'auth/2fa_trusted_devices.html',
        devices=devices,
        csrf_token=csrf_token
    )

@two_factor_bp.route('/trusted-devices/remove/<int:device_id>', methods=['POST'])
@login_required
def remove_trusted_device(device_id):
    """Remove a trusted device"""
    if not current_user.requires_2fa:
        flash('You need to enable two-factor authentication first.', 'warning')
        return redirect(url_for('two_factor.setup'))
    
    # Verify CSRF token
    if not session.get('csrf_token') or session.get('csrf_token') != request.form.get('csrf_token'):
        flash('Invalid request. Please try again.', 'danger')
        return redirect(url_for('two_factor.trusted_devices'))
    
    # Get the device
    from models.security_models import TrustedDevice
    
    device = TrustedDevice.query.filter_by(
        id=device_id,
        user_id=current_user.id
    ).first()
    
    if not device:
        flash('Device not found.', 'danger')
        return redirect(url_for('two_factor.trusted_devices'))
    
    # Remove the device
    try:
        device.is_trusted = False
        db.session.commit()
        
        # Log the event
        log_security_event(
            'trusted_device_removed', 
            current_user.id, 
            f"Trusted device removed for {current_user.email}: {device.name}",
            request.remote_addr
        )
        
        flash('Device has been removed from trusted devices.', 'success')
        return redirect(url_for('two_factor.trusted_devices'))
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error removing trusted device: {str(e)}")
        flash('An error occurred. Please try again.', 'danger')
        return redirect(url_for('two_factor.trusted_devices'))