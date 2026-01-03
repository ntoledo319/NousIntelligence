"""
CSRF Protection Validator
Complete CSRF validation for all state-changing endpoints
"""
from flask import request, session, abort
from functools import wraps
import logging

logger = logging.getLogger(__name__)


def validate_csrf_token():
    """
    Validate CSRF token for state-changing requests.
    Should be called in before_request or as decorator.
    """
    # Skip for safe methods
    if request.method in ['GET', 'HEAD', 'OPTIONS']:
        return
    
    # Skip for health/status endpoints
    if request.endpoint and ('health' in request.endpoint or 'status' in request.endpoint):
        return
    
    # Get token from form or header
    token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
    session_token = session.get('csrf_token')
    
    if not session_token:
        logger.warning(f"CSRF validation failed: No session token for {request.endpoint}")
        abort(403, description="CSRF token missing from session")
    
    if not token:
        logger.warning(f"CSRF validation failed: No token in request to {request.endpoint}")
        abort(403, description="CSRF token missing from request")
    
    if token != session_token:
        logger.warning(f"CSRF validation failed: Token mismatch for {request.endpoint}")
        abort(403, description="CSRF token invalid")


def csrf_exempt(f):
    """
    Decorator to exempt specific endpoints from CSRF validation.
    Use sparingly - only for external API callbacks where CSRF isn't applicable.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    
    decorated_function._csrf_exempt = True
    return decorated_function


def require_csrf(f):
    """
    Decorator to explicitly require CSRF validation.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        validate_csrf_token()
        return f(*args, **kwargs)
    
    return decorated_function
