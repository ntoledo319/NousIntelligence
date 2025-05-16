"""
API Key Management Module

This module provides utilities for API key generation, validation, rotation,
and lifecycle management to enhance security through regular key rotation.

@module: api_key_manager
@author: NOUS Development Team
"""
import os
import secrets
import string
import hashlib
import logging
import time  # Added missing time module
from datetime import datetime, timedelta
import json
from typing import Dict, Any, Optional, Tuple, List, Union
from functools import wraps

from flask import request, jsonify, g, current_app
from sqlalchemy.exc import SQLAlchemyError

from models import db, APIKey, APIKeyEvent, User

# Configure logger
logger = logging.getLogger(__name__)

# Constants for API key generation and validation
API_KEY_PREFIX_LENGTH = 8
API_KEY_SECRET_LENGTH = 32
API_KEY_SEPARATOR = '.'
DEFAULT_EXPIRY_DAYS = 90  # Default expiry for keys (3 months)
ROTATION_GRACE_PERIOD_DAYS = 7  # Old keys remain valid for this many days after rotation
DEFAULT_SCOPES = ["read"]  # Default scopes for new keys
AVAILABLE_SCOPES = ["read", "write", "admin", "user", "system", "analytics", "billing"]

class APIKeyError(Exception):
    """Base exception for API key errors"""
    pass

class APIKeyInvalidError(APIKeyError):
    """Raised when an API key is invalid"""
    pass

class APIKeyExpiredError(APIKeyError):
    """Raised when an API key has expired"""
    pass

class APIKeyScopeError(APIKeyError):
    """Raised when an API key lacks the required scope"""
    pass

class APIKeyRotationError(APIKeyError):
    """Raised when there's an error rotating an API key"""
    pass

class APIKeyRateLimitError(APIKeyError):
    """Raised when rate limits are exceeded"""
    pass

def generate_api_key() -> Tuple[str, str, str]:
    """
    Generate a new API key in the format prefix.secret
    
    Returns:
        Tuple of (full_key, prefix, secret)
    """
    # Generate a random prefix (visible part for identification)
    prefix = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(API_KEY_PREFIX_LENGTH))
    
    # Generate a secure random secret (hidden part)
    secret = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(API_KEY_SECRET_LENGTH))
    
    # Combine to create the full key
    full_key = f"{prefix}{API_KEY_SEPARATOR}{secret}"
    
    return full_key, prefix, secret

def hash_api_key(key: str) -> str:
    """
    Hash an API key for secure storage
    
    Args:
        key: The API key to hash
        
    Returns:
        Secure hash of the key
    """
    # Use a strong hashing algorithm (SHA-256)
    hash_obj = hashlib.sha256(key.encode())
    return hash_obj.hexdigest()

def validate_api_key(key: str) -> Optional[APIKey]:
    """
    Validate an API key and return the associated key object if valid
    
    Args:
        key: The API key to validate
        
    Returns:
        APIKey object if valid, None otherwise
        
    Raises:
        APIKeyInvalidError: If key format is invalid
        APIKeyExpiredError: If key has expired
    """
    # Check key format
    try:
        prefix, secret = key.split(API_KEY_SEPARATOR, 1)
        if len(prefix) != API_KEY_PREFIX_LENGTH:
            raise APIKeyInvalidError("Invalid API key format")
    except ValueError:
        raise APIKeyInvalidError("Invalid API key format")
    
    # Find the key in the database
    api_key = APIKey.query.filter_by(key_prefix=prefix, status='active').first()
    
    if not api_key:
        # Also check rotated keys in grace period
        grace_period = datetime.utcnow() - timedelta(days=ROTATION_GRACE_PERIOD_DAYS)
        api_key = APIKey.query.filter_by(
            key_prefix=prefix, 
            status='rotated'
        ).filter(
            APIKey.last_rotated_at >= grace_period
        ).first()
        
        if not api_key:
            raise APIKeyInvalidError("API key not found or no longer active")
    
    # Verify the key hash
    full_key = f"{prefix}{API_KEY_SEPARATOR}{secret}"
    if api_key.key_hash != hash_api_key(full_key):
        raise APIKeyInvalidError("Invalid API key")
    
    # Check expiration
    if api_key.expires_at and api_key.expires_at < datetime.utcnow():
        raise APIKeyExpiredError("API key has expired")
    
    # Record usage
    try:
        api_key.record_usage()
        db.session.commit()
    except SQLAlchemyError as e:
        logger.warning(f"Failed to update API key usage stats: {str(e)}")
        db.session.rollback()
    
    return api_key

def check_api_key_scope(api_key: APIKey, required_scope: str) -> bool:
    """
    Check if an API key has the required scope
    
    Args:
        api_key: The API key to check
        required_scope: The required scope
        
    Returns:
        True if the key has the required scope, False otherwise
    """
    return api_key.has_scope(required_scope)

def create_api_key(
    user_id: int,
    name: str,
    scopes: Optional[List[str]] = None,
    expires_in_days: Optional[int] = None,
    request_info: Optional[Dict] = None
) -> Tuple[APIKey, str]:
    """
    Create a new API key for a user
    
    Args:
        user_id: User ID to create the key for
        name: User-defined name for the key
        scopes: List of scopes to grant (defaults to ["read"])
        expires_in_days: Days until expiration (defaults to 90 days)
        request_info: Optional request information for auditing
        
    Returns:
        Tuple of (APIKey object, full_key)
    """
    # Validate scopes
    if scopes is None:
        scopes = DEFAULT_SCOPES.copy()
    else:
        # Ensure all scopes are valid
        for scope in scopes:
            if scope != '*' and scope not in AVAILABLE_SCOPES:
                raise ValueError(f"Invalid scope: {scope}")
    
    # Generate expiry date
    if expires_in_days is None:
        expires_in_days = DEFAULT_EXPIRY_DAYS
    
    if expires_in_days > 0:
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
    else:
        expires_at = None  # No expiration
    
    # Generate new API key
    full_key, prefix, secret = generate_api_key()
    key_hash = hash_api_key(full_key)
    
    # Create API key record
    api_key = APIKey(
        user_id=user_id,
        name=name,
        key_prefix=prefix,
        key_hash=key_hash,
        scopes=json.dumps(scopes),
        expires_at=expires_at,
        status='active'
    )
    
    try:
        db.session.add(api_key)
        db.session.flush()  # Get ID without committing
        
        # Record creation event
        event = APIKeyEvent(
            api_key_id=api_key.id,
            event_type='created',
            performed_by_id=user_id
        )
        
        # Add request info if available
        if request_info:
            event.ip_address = request_info.get('ip_address')
            event.user_agent = request_info.get('user_agent')
            if request_info.get('metadata'):
                event.metadata = json.dumps(request_info['metadata'])
        
        db.session.add(event)
        db.session.commit()
        
        logger.info(f"Created new API key {prefix}... for user {user_id}")
        
        return api_key, full_key
    
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error creating API key: {str(e)}")
        raise
    
def revoke_api_key(
    api_key_id: int,
    performed_by_id: int,
    request_info: Optional[Dict] = None
) -> bool:
    """
    Revoke an API key
    
    Args:
        api_key_id: ID of the key to revoke
        performed_by_id: ID of the user performing the revocation
        request_info: Optional request information for auditing
        
    Returns:
        True if successful
    """
    api_key = APIKey.query.get(api_key_id)
    if not api_key:
        raise APIKeyError("API key not found")
    
    # Check if user is authorized to revoke this key
    user = User.query.get(performed_by_id)
    if not user.is_administrator() and api_key.user_id != performed_by_id:
        raise APIKeyError("Not authorized to revoke this API key")
    
    try:
        # Update key status
        api_key.status = 'revoked'
        
        # Record revocation event
        event = APIKeyEvent(
            api_key_id=api_key.id,
            event_type='revoked',
            performed_by_id=performed_by_id
        )
        
        # Add request info if available
        if request_info:
            event.ip_address = request_info.get('ip_address')
            event.user_agent = request_info.get('user_agent')
            if request_info.get('metadata'):
                event.metadata = json.dumps(request_info['metadata'])
        
        db.session.add(event)
        db.session.commit()
        
        logger.info(f"Revoked API key {api_key.key_prefix}... (ID: {api_key.id})")
        
        return True
    
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error revoking API key: {str(e)}")
        raise

def rotate_api_key(
    api_key_id: int,
    performed_by_id: int,
    request_info: Optional[Dict] = None
) -> Tuple[APIKey, str]:
    """
    Rotate an API key by creating a new key and marking the old one as rotated
    The old key remains valid for a grace period to allow for system updates
    
    Args:
        api_key_id: ID of the key to rotate
        performed_by_id: ID of the user performing the rotation
        request_info: Optional request information for auditing
        
    Returns:
        Tuple of (new APIKey object, new full_key)
    """
    old_key = APIKey.query.get(api_key_id)
    if not old_key:
        raise APIKeyRotationError("API key not found")
    
    # Check if key is active
    if old_key.status != 'active':
        raise APIKeyRotationError("Cannot rotate an already rotated or revoked key")
    
    # Check if user is authorized to rotate this key
    user = User.query.get(performed_by_id)
    if not user.is_administrator() and old_key.user_id != performed_by_id:
        raise APIKeyRotationError("Not authorized to rotate this API key")
    
    try:
        # Generate new API key
        full_key, prefix, secret = generate_api_key()
        key_hash = hash_api_key(full_key)
        
        # Parse old scopes
        scopes = json.loads(old_key.scopes) if isinstance(old_key.scopes, str) else old_key.scopes
        
        # Create new key with same parameters
        new_key = APIKey(
            user_id=old_key.user_id,
            name=f"{old_key.name} (rotated)",
            key_prefix=prefix,
            key_hash=key_hash,
            scopes=json.dumps(scopes),
            expires_at=old_key.expires_at,
            status='active',
            rotated_from_id=old_key.id,
            rotation_count=old_key.rotation_count + 1
        )
        
        db.session.add(new_key)
        db.session.flush()  # Get ID without committing
        
        # Update old key
        old_key.status = 'rotated'
        old_key.rotated_to_id = new_key.id
        old_key.last_rotated_at = datetime.utcnow()
        
        # Record rotation events
        rotation_event = APIKeyEvent(
            api_key_id=old_key.id,
            event_type='rotated',
            performed_by_id=performed_by_id
        )
        
        creation_event = APIKeyEvent(
            api_key_id=new_key.id,
            event_type='created',
            performed_by_id=performed_by_id,
            metadata=json.dumps({"rotated_from": old_key.id})
        )
        
        # Add request info if available
        if request_info:
            rotation_event.ip_address = request_info.get('ip_address')
            rotation_event.user_agent = request_info.get('user_agent')
            creation_event.ip_address = request_info.get('ip_address')
            creation_event.user_agent = request_info.get('user_agent')
        
        db.session.add(rotation_event)
        db.session.add(creation_event)
        db.session.commit()
        
        logger.info(f"Rotated API key {old_key.key_prefix}... to {new_key.key_prefix}...")
        
        return new_key, full_key
    
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error rotating API key: {str(e)}")
        raise

def check_rate_limits(api_key: APIKey, hourly_limit: int = 1000, daily_limit: int = 10000) -> bool:
    """
    Check if an API key has exceeded its rate limits
    
    Args:
        api_key: The API key to check
        hourly_limit: Maximum requests per hour
        daily_limit: Maximum requests per day
        
    Returns:
        True if within limits, False if exceeded
        
    Raises:
        APIKeyRateLimitError: If rate limit is exceeded
    """
    # Reset counters if needed
    now = datetime.utcnow()
    
    # Check hourly rate limit
    hourly_diff = now - api_key.hourly_reset_at
    if hourly_diff.total_seconds() > 3600:
        api_key.hourly_usage = 0
        api_key.hourly_reset_at = now
    elif api_key.hourly_usage >= hourly_limit:
        next_reset = api_key.hourly_reset_at + timedelta(hours=1)
        reset_in = int((next_reset - now).total_seconds())
        raise APIKeyRateLimitError(f"Hourly rate limit exceeded. Resets in {reset_in} seconds")
    
    # Check daily rate limit
    daily_diff = now - api_key.daily_reset_at
    if daily_diff.total_seconds() > 86400:
        api_key.daily_usage = 0
        api_key.daily_reset_at = now
    elif api_key.daily_usage >= daily_limit:
        next_reset = api_key.daily_reset_at + timedelta(days=1)
        reset_in = int((next_reset - now).total_seconds())
        raise APIKeyRateLimitError(f"Daily rate limit exceeded. Resets in {reset_in} seconds")
    
    return True

def init_api_key_cleanup(app):
    """
    Initialize scheduled cleanup of expired API keys and rotation grace periods
    
    Args:
        app: Flask application instance
    """
    import threading
    
    def cleanup_worker():
        """Worker function to periodically clean up API keys"""
        with app.app_context():
            while True:
                try:
                    # Update expired keys
                    now = datetime.utcnow()
                    expired_keys = APIKey.query.filter(
                        APIKey.status == 'active',
                        APIKey.expires_at < now
                    ).all()
                    
                    for key in expired_keys:
                        key.status = 'expired'
                        
                        # Create expired event
                        event = APIKeyEvent(
                            api_key_id=key.id,
                            event_type='expired'
                        )
                        db.session.add(event)
                    
                    # Mark rotated keys as expired after grace period
                    grace_cutoff = now - timedelta(days=ROTATION_GRACE_PERIOD_DAYS)
                    rotated_keys = APIKey.query.filter(
                        APIKey.status == 'rotated',
                        APIKey.last_rotated_at < grace_cutoff
                    ).all()
                    
                    for key in rotated_keys:
                        key.status = 'expired'
                        
                        # Create expired event
                        event = APIKeyEvent(
                            api_key_id=key.id,
                            event_type='expired',
                            metadata=json.dumps({"reason": "rotation_grace_period_ended"})
                        )
                        db.session.add(event)
                    
                    if expired_keys or rotated_keys:
                        db.session.commit()
                        logger.info(f"Cleaned up {len(expired_keys)} expired and {len(rotated_keys)} rotated API keys")
                    
                except Exception as e:
                    logger.error(f"Error in API key cleanup: {str(e)}")
                    db.session.rollback()
                
                # Sleep for 1 hour
                time.sleep(3600)
    
    # Start cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
    cleanup_thread.start()
    
    logger.info("API key cleanup scheduler initialized")

def api_key_required(f=None, scopes=None):
    """
    Decorator to protect routes with API key authentication
    
    Args:
        f: The function to decorate
        scopes: Required scopes (single string or list of strings)
        
    Returns:
        Decorated function that requires a valid API key
    """
    if f is None:
        return lambda f: api_key_required(f, scopes=scopes)
    
    required_scopes = []
    if scopes:
        if isinstance(scopes, str):
            required_scopes = [scopes]
        else:
            required_scopes = scopes
    
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get API key from request
        api_key_value = None
        
        # Check Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            api_key_value = auth_header.split('Bearer ')[1]
        
        # Check X-API-Key header
        if not api_key_value:
            api_key_value = request.headers.get('X-API-Key')
        
        # Check query parameter
        if not api_key_value:
            api_key_value = request.args.get('api_key')
        
        if not api_key_value:
            return jsonify({
                'error': 'Authentication required',
                'message': 'API key is required'
            }), 401
        
        try:
            # Validate API key
            api_key = validate_api_key(api_key_value)
            
            # Check rate limits
            check_rate_limits(api_key)
            
            # Check scopes if required
            if required_scopes:
                has_required_scope = False
                for scope in required_scopes:
                    if check_api_key_scope(api_key, scope):
                        has_required_scope = True
                        break
                
                if not has_required_scope:
                    return jsonify({
                        'error': 'Insufficient permissions',
                        'message': f'API key is missing required scope. Needs one of: {", ".join(required_scopes)}'
                    }), 403
            
            # Store API key and user ID in flask.g for use in the route
            g.api_key = api_key
            g.user_id = api_key.user_id
            
            return f(*args, **kwargs)
        
        except APIKeyInvalidError as e:
            return jsonify({
                'error': 'Invalid API key',
                'message': str(e)
            }), 401
        
        except APIKeyExpiredError as e:
            return jsonify({
                'error': 'Expired API key',
                'message': str(e)
            }), 401
        
        except APIKeyScopeError as e:
            return jsonify({
                'error': 'Insufficient permissions',
                'message': str(e)
            }), 403
        
        except APIKeyRateLimitError as e:
            return jsonify({
                'error': 'Rate limit exceeded',
                'message': str(e)
            }), 429
    
    return decorated

def get_request_info() -> Dict[str, Any]:
    """
    Get information about the current request for auditing purposes
    
    Returns:
        Dictionary with request information
    """
    return {
        'ip_address': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', ''),
        'metadata': {
            'endpoint': request.endpoint,
            'method': request.method,
            'path': request.path,
            'referrer': request.referrer
        }
    } 