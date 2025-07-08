"""
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated
Two Factor Routes Routes
Two Factor Routes functionality for the NOUS application
"""

from flask import Blueprint, render_template, session, request, redirect, url_for, jsonify
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated

two_factor_routes_bp = Blueprint('two_factor_routes', __name__)


def require_authentication():
    """Check if user is authenticated, allow demo mode"""
    from flask import session, request, redirect, url_for, jsonify
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated
    
    # Check session authentication
    if 'user' in session and session['user']:
        return None  # User is authenticated
    
    # Allow demo mode
    if request.args.get('demo') == 'true':
        return None  # Demo mode allowed
    
    # For API endpoints, return JSON error
    if request.path.startswith('/api/'):
        return jsonify({'error': "Demo mode - limited access", 'demo_available': True}), 401
    
    # For web routes, redirect to login
    return redirect(url_for("main.demo"))

def get_get_demo_user()():
    """Get current user from session with demo fallback"""
    from flask import session
    return session.get('user', {
        'id': 'demo_user',
        'name': 'Demo User',
        'email': 'demo@example.com',
        'is_demo': True
    })

def is_authenticated():
    """Check if user is authenticated"""
    from flask import session
    return 'user' in session and session['user'] is not None

Two-Factor Authentication Routes

This module provides routes for setting up, verifying, and managing
two-factor authentication (2FA) for user accounts.

@module: two_factor_routes
@author: NOUS Development Team
"""
import logging
from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for, g, flash

from werkzeug.exceptions import BadRequest, Unauthorized

from utils.two_factor_auth import (
    setup_2fa_session,
    confirm_2fa_setup,
    verify_totp,
    verify_backup_code,
    get_totp_uri,
    generate_qr_code,
    TOTPVerificationError
)
from utils.security_helper import (
    rate_limit,
    sanitize_input
)
from utils.schema_validation import validate_with_schema

# Import your user model
from models import User, TwoFactorBackupCode, db

# Create blueprint
two_factor_bp = Blueprint('two_factor', __name__, url_prefix='/2fa')

# Configure logger
logger = logging.getLogger(__name__)

@two_factor_bp.route('/setup', methods=['GET', 'POST'])
@rate_limit(max_requests=5, time_window=60)
def setup_2fa():
    """
    Setup two-factor authentication for the current user

    GET: Returns setup page with QR code
    POST: Confirms setup with verification code
    """
    user = session.get('user')

    # Check if 2FA is already enabled
    if user.two_factor_enabled:
        flash("Two-factor authentication is already enabled", "info")
        return redirect(url_for('user.profile'))

    if request.method == 'GET':
        # Initialize 2FA setup
        setup_data = setup_2fa_session(user.id)
        secret = setup_data['secret']
        backup_codes = setup_data['backup_codes']

        # Generate QR code URI
        totp_uri = get_totp_uri(secret, user.email)
        qr_code = generate_qr_code(totp_uri)

        # Convert QR code to data URL
        import base64
        qr_code_b64 = base64.b64encode(qr_code).decode('utf-8')
        qr_code_data_url = f"data:image/png;base64,{qr_code_b64}"

        # Render setup page
        return render_template(
            '2fa/setup.html',
            qr_code=qr_code_data_url,
            secret=secret,
            backup_codes=backup_codes
        )

    elif request.method == 'POST':
        # Confirm 2FA setup
        verification_code = sanitize_input(request.form.get('verification_code'))

        if not verification_code:
            flash("Verification code is required", "error")
            return redirect(url_for('two_factor.setup_2fa'))

        try:
            # Confirm setup
            confirm_2fa_setup(verification_code)

            # Get setup data from session
            setup_data = session.pop('2fa_setup')
            secret = setup_data['secret']
            backup_codes_hashes = setup_data['backup_codes']

            # Save to database
            user.two_factor_secret = secret
            user.two_factor_enabled = True

            # Save backup codes
            for code_hash in backup_codes_hashes:
                backup_code = TwoFactorBackupCode(
                    user_id=user.id,
                    code_hash=code_hash,
                    used=False
                )
                db.session.add(backup_code)

            db.session.commit()

            # Mark session as 2FA verified
            session['2fa_verified'] = True

            flash("Two-factor authentication has been enabled", "success")
            return redirect(url_for('user.profile'))

        except TOTPVerificationError as e:
            flash(f"Verification failed: {str(e)}", "error")
            return redirect(url_for('two_factor.setup_2fa'))

@two_factor_bp.route('/verify', methods=['GET', 'POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def verify_2fa():
    """
    Verify a 2FA code

    GET: Show 2FA verification form
    POST: Verify code and continue to original destination
    """
    # Check if user is logged in
    if not ('user' in session and session['user']):
        return redirect(url_for("main.demo"))

    # Check if 2FA is already verified for this session
    if session.get('2fa_verified'):
        # Already verified, proceed to destination
        next_url = session.pop('after_2fa_url', url_for('user.profile'))
        return redirect(next_url)

    user = session.get('user')

    # Check if 2FA is enabled for this user
    if not user.two_factor_enabled:
        # Not enabled, proceed
        session['2fa_verified'] = True
        next_url = session.pop('after_2fa_url', url_for('user.profile'))
        return redirect(next_url)

    if request.method == 'GET':
        return render_template('2fa/verify.html')

    elif request.method == 'POST':
        # Get code from form
        verification_type = request.form.get('verification_type', 'totp')
        code = sanitize_input(request.form.get('code'))

        if not code:
            flash("Verification code is required", "error")
            return render_template('2fa/verify.html')

        # Verify code
        verified = False

        if verification_type == 'totp':
            # Verify TOTP code
            if verify_totp(user.two_factor_secret, code):
                verified = True

        elif verification_type == 'backup':
            # Try to find and verify a matching backup code
            backup_codes = TwoFactorBackupCode.query.filter_by(
                user_id=user.id,
                used=False
            ).all()

            for backup_code in backup_codes:
                if verify_backup_code(code, backup_code.code_hash):
                    # Mark code as used
                    backup_code.used = True
                    db.session.commit()
                    verified = True
                    break

        if verified:
            # Mark session as 2FA verified
            session['2fa_verified'] = True

            # Redirect to original destination or default
            next_url = session.pop('after_2fa_url', url_for('user.profile'))
            return redirect(next_url)
        else:
            flash("Invalid verification code", "error")
            return render_template('2fa/verify.html')

@two_factor_bp.route('/disable', methods=['POST'])
@rate_limit(max_requests=5, time_window=60)
def disable_2fa():
    """Disable 2FA for the current user"""
    user = session.get('user')

    # Check if 2FA is enabled
    if not user.two_factor_enabled:
        flash("Two-factor authentication is not enabled", "info")
        return redirect(url_for('user.profile'))

    # Verify password
    password = request.form.get('password')
    if not user.check_password(password):
        flash("Invalid password", "error")
        return redirect(url_for('user.profile'))

    # Disable 2FA
    user.two_factor_enabled = False
    user.two_factor_secret = None

    # Delete backup codes
    TwoFactorBackupCode.query.filter_by(user_id=user.id).delete()

    db.session.commit()

    # Remove 2FA verification from session
    session.pop('2fa_verified', None)

    flash("Two-factor authentication has been disabled", "success")
    return redirect(url_for('user.profile'))

@two_factor_bp.route('/regenerate-backup-codes', methods=['POST'])
@rate_limit(max_requests=5, time_window=60)
def regenerate_backup_codes():
    """Generate new backup codes and invalidate old ones"""
    user = session.get('user')

    # Check if 2FA is enabled
    if not user.two_factor_enabled:
        flash("Two-factor authentication is not enabled", "info")
        return redirect(url_for('user.profile'))

    # Verify password
    password = request.form.get('password')
    if not user.check_password(password):
        flash("Invalid password", "error")
        return redirect(url_for('user.profile'))

    # Delete existing backup codes
    TwoFactorBackupCode.query.filter_by(user_id=user.id).delete()

    # Generate new backup codes
    backup_codes = []
    from utils.two_factor_auth import generate_backup_codes, hash_backup_code

    new_codes = generate_backup_codes()

    # Save new backup codes
    for code in new_codes:
        code_hash = hash_backup_code(code)
        backup_code = TwoFactorBackupCode(
            user_id=user.id,
            code_hash=code_hash,
            used=False
        )
        db.session.add(backup_code)
        backup_codes.append(code)

    db.session.commit()

    # Show new codes to user
    return render_template(
        '2fa/backup_codes.html',
        backup_codes=backup_codes
    )

# API routes for 2FA (used by mobile/SPA clients)
@two_factor_bp.route('/api/setup', methods=['POST'])
@rate_limit(max_requests=5, time_window=60)
def api_setup_2fa():
    """API endpoint to setup 2FA (step 1)"""
    user = session.get('user')

    # Check if 2FA is already enabled
    if user.two_factor_enabled:
        return jsonify({
            "error": "2FA already enabled",
            "message": "Two-factor authentication is already enabled for this account"
        }), 400

    # Initialize 2FA setup
    setup_data = setup_2fa_session(user.id)
    secret = setup_data['secret']
    backup_codes = setup_data['backup_codes']

    # Generate QR code URI
    totp_uri = get_totp_uri(secret, user.email)

    # Return setup data
    return jsonify({
        "secret": secret,
        "totp_uri": totp_uri,
        "backup_codes": backup_codes
    })

@two_factor_bp.route('/api/confirm', methods=['POST'])
@rate_limit(max_requests=5, time_window=60)
def api_confirm_2fa():
    """API endpoint to confirm 2FA setup (step 2)"""
    user = session.get('user')
    data = request.get_json()

    if not data or 'verification_code' not in data:
        return jsonify({
            "error": "Missing data",
            "message": "Verification code is required"
        }), 400

    verification_code = sanitize_input(data['verification_code'])

    try:
        # Confirm setup
        confirm_2fa_setup(verification_code)

        # Get setup data from session
        setup_data = session.pop('2fa_setup')
        secret = setup_data['secret']
        backup_codes_hashes = setup_data['backup_codes']

        # Save to database
        user.two_factor_secret = secret
        user.two_factor_enabled = True

        # Save backup codes
        for code_hash in backup_codes_hashes:
            backup_code = TwoFactorBackupCode(
                user_id=user.id,
                code_hash=code_hash,
                used=False
            )
            db.session.add(backup_code)

        db.session.commit()

        # Mark session as 2FA verified
        session['2fa_verified'] = True

        return jsonify({
            "success": True,
            "message": "Two-factor authentication has been enabled"
        })

    except TOTPVerificationError as e:
        return jsonify({
            "error": "Verification failed",
            "message": str(e)
        }), 400

@two_factor_bp.route('/api/verify', methods=['POST'])
def api_verify_2fa():
    """API endpoint to verify a 2FA code"""
    # Check if user is logged in
    if not ('user' in session and session['user']):
        return jsonify({
            "error": "Demo mode - limited access",
            "message": "Demo mode - some features limited"
        }), 401

    user = session.get('user')
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Missing data",
            "message": "Verification code is required"
        }), 400

    verification_type = data.get('verification_type', 'totp')
    code = sanitize_input(data.get('code'))

    if not code:
        return jsonify({
            "error": "Missing code",
            "message": "Verification code is required"
        }), 400

    # Verify code
    verified = False

    if verification_type == 'totp':
        # Verify TOTP code
        if verify_totp(user.two_factor_secret, code):
            verified = True

    elif verification_type == 'backup':
        # Try to find and verify a matching backup code
        backup_codes = TwoFactorBackupCode.query.filter_by(
            user_id=user.id,
            used=False
        ).all()

        for backup_code in backup_codes:
            if verify_backup_code(code, backup_code.code_hash):
                # Mark code as used
                backup_code.used = True
                db.session.commit()
                verified = True
                break

    if verified:
        # Mark session as 2FA verified
        session['2fa_verified'] = True

        return jsonify({
            "success": True,
            "message": "Two-factor authentication verified"
        })
    else:
        return jsonify({
            "error": "Invalid code",
            "message": "Invalid verification code"
        }), 400