"""
Authentication API Routes

This module provides API endpoints for JWT authentication, including login,
token refresh, and logout functionality.

@module: auth_api
@author: NOUS Development Team
"""
import logging
from flask import Blueprint, request, jsonify, g
from flask_login import current_user, login_user, logout_user
from werkzeug.exceptions import BadRequest, Unauthorized

from utils.jwt_auth import (
    generate_jwt_token,
    validate_jwt_token,
    blacklist_token,
    jwt_required,
    refresh_token_required
)
from utils.security_helper import (
    rate_limit,
    record_failed_login,
    reset_failed_login,
    is_account_locked,
    sanitize_input
)
from utils.schema_validation import validate_with_schema

# Import your user model
from models import User, db

# Create blueprint
auth_api = Blueprint('auth_api', __name__, url_prefix='/api/auth')

# Configure logger
logger = logging.getLogger(__name__)

@auth_api.route('/login', methods=['POST'])
@rate_limit(max_requests=5, time_window=60)
@validate_with_schema("login")
def login():
    """
    Generate JWT tokens for a user

    Request JSON:
    {
        "email": "user@example.com",
        "password": "secure_password"
    }

    Response:
    {
        "access_token": "eyJhbGciOiJ...",
        "refresh_token": "eyJhbGciOiJ...",
        "expires_at": 1623456789,
        "token_type": "Bearer"
    }
    """
    # Get login credentials
    data = request.get_json()

    email = sanitize_input(data.get('email', ''))
    password = data.get('password', '')

    # Check if account is locked
    is_locked, minutes_left = is_account_locked(email)
    if is_locked:
        return jsonify({
            "error": "Account locked",
            "message": f"Account is temporarily locked. Try again in {minutes_left} minutes."
        }), 403

    # Attempt to authenticate
    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        # Record failed login attempt
        record_failed_login(email)

        return jsonify({
            "error": "Authentication failed",
            "message": "Invalid email or password"
        }), 401

    # Reset failed login attempts
    reset_failed_login(email)

    # Generate tokens
    access_token, access_expires = generate_jwt_token(user.id, 'access')
    refresh_token, refresh_expires = generate_jwt_token(user.id, 'refresh')

    # Update last login timestamp
    user.last_login = db.func.now()
    db.session.commit()

    # Log successful login
    logger.info(f"User {user.id} ({user.email}) logged in via JWT")

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": access_expires,
        "token_type": "Bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    })

@auth_api.route('/refresh', methods=['POST'])
@refresh_token_required
@rate_limit(max_requests=10, time_window=60)
@validate_with_schema("refresh_token")
def refresh():
    """
    Refresh an access token using a refresh token

    Request Header:
    Authorization: Bearer <refresh_token>

    Response:
    {
        "access_token": "eyJhbGciOiJ...",
        "expires_at": 1623456789,
        "token_type": "Bearer"
    }
    """
    # Get user ID from g (set by refresh_token_required decorator)
    user_id = g.user_id

    # Generate new access token
    access_token, access_expires = generate_jwt_token(user_id, 'access')

    # Log token refresh
    logger.info(f"Refreshed access token for user {user_id}")

    return jsonify({
        "access_token": access_token,
        "expires_at": access_expires,
        "token_type": "Bearer"
    })

@auth_api.route('/logout', methods=['POST'])
@jwt_required
def logout():
    """
    Invalidate the current JWT token

    Request Header:
    Authorization: Bearer <access_token>

    Response:
    {
        "message": "Logged out successfully"
    }
    """
    # Get token
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split('Bearer ')[1]

        # Blacklist the token
        blacklist_token(token)

        # Log logout
        logger.info(f"User {g.user_id} logged out")

        return jsonify({
            "message": "Logged out successfully"
        })

    return jsonify({
        "message": "No token to invalidate"
    })

@auth_api.route('/check', methods=['GET'])
@jwt_required
def check_auth():
    """
    Check if a JWT token is valid

    Request Header:
    Authorization: Bearer <access_token>

    Response:
    {
        "authenticated": true,
        "user_id": 123
    }
    """
    return jsonify({
        "authenticated": True,
        "user_id": g.user_id
    })

# Register error handlers
@auth_api.errorhandler(BadRequest)
def handle_bad_request(error):
    """Handle bad request errors"""
    response = jsonify({
        "error": "Bad Request",
        "message": str(error.description)
    })
    response.status_code = 400
    return response

@auth_api.errorhandler(Unauthorized)
def handle_unauthorized(error):
    """Handle unauthorized errors"""
    response = jsonify({
        "error": "Unauthorized",
        "message": str(error.description)
    })
    response.status_code = 401
    return response