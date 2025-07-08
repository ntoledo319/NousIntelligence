"""
API Key Management Routes

This module provides API endpoints for creating, rotating, and managing API keys
for secure access to the NOUS API.

@module: api_key_routes
@author: NOUS Development Team
"""
import logging
from flask import Blueprint, request, jsonify, g
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated
from werkzeug.exceptions import BadRequest, Unauthorized, Forbidden
import json
from datetime import datetime

from utils.api_key_manager import (
    create_api_key,
    rotate_api_key,
    revoke_api_key,
    get_request_info,
    api_key_required,
    APIKeyError,
    APIKeyRotationError,
    AVAILABLE_SCOPES,
    DEFAULT_EXPIRY_DAYS
)
from utils.security_helper import rate_limit
from utils.schema_validation import validate_with_schema
from models import db, APIKey, APIKeyEvent

# Create blueprint
api_key_bp = Blueprint('api_key', __name__, url_prefix='/api/keys')

# Configure logger
logger = logging.getLogger(__name__)

@api_key_bp.route('/', methods=['GET'])
@login_required
@rate_limit(max_requests=30, time_window=60)
def list_keys():
    """
    List all API keys belonging to the current user

    Response:
    {
        "keys": [
            {
                "id": 1,
                "name": "My API Key",
                "key_prefix": "abcd1234...",
                "status": "active",
                "scopes": ["read", "write"],
                "created_at": "2023-10-03T12:00:00Z",
                "expires_at": "2023-12-31T12:00:00Z",
                "rotation_count": 0
            }
        ]
    }
    """
    # Get keys for current user
    api_keys = APIKey.query.filter_by(user_id=get_current_user().get("id") if get_current_user() else None).all()

    # Format response
    keys = [key.to_dict() for key in api_keys]

    return jsonify({
        "keys": keys
    })

@api_key_bp.route('/<int:key_id>', methods=['GET'])
@login_required
@rate_limit(max_requests=30, time_window=60)
def get_key(key_id):
    """
    Get details of a specific API key

    Response:
    {
        "key": {
            "id": 1,
            "name": "My API Key",
            "key_prefix": "abcd1234...",
            "status": "active",
            "scopes": ["read", "write"],
            "created_at": "2023-10-03T12:00:00Z",
            "expires_at": "2023-12-31T12:00:00Z",
            "rotation_count": 0,
            "last_used_at": "2023-10-03T12:00:00Z",
            "use_count": 10,
            "last_rotated_at": null,
            "hourly_usage": 5,
            "daily_usage": 10
        }
    }
    """
    # Get key by ID
    api_key = APIKey.query.get_or_404(key_id)

    # Check authorization (must be owner or admin)
    if api_key.user_id != get_current_user().get("id") if get_current_user() else None and not current_user.is_administrator():
        return jsonify({
            "error": "Forbidden",
            "message": "You do not have permission to view this API key"
        }), 403

    # Format response with full metadata
    return jsonify({
        "key": api_key.to_dict(include_metadata=True)
    })

@api_key_bp.route('/', methods=['POST'])
@login_required
@rate_limit(max_requests=10, time_window=60)
@validate_with_schema("create_api_key")
def create_key():
    """
    Create a new API key

    Request:
    {
        "name": "My API Key",
        "scopes": ["read", "write"],
        "expires_in_days": 90
    }

    Response:
    {
        "key": {
            "id": 1,
            "name": "My API Key",
            "key_prefix": "abcd1234...",
            "status": "active",
            "scopes": ["read", "write"],
            "created_at": "2023-10-03T12:00:00Z",
            "expires_at": "2023-12-31T12:00:00Z"
        },
        "api_key": "abcd1234.SECRET_PART" // Only shown once
    }
    """
    data = request.get_json()

    # Extract parameters
    name = data.get('name', 'API Key')
    scopes = data.get('scopes', None)
    expires_in_days = data.get('expires_in_days', DEFAULT_EXPIRY_DAYS)

    # Get request info for auditing
    request_info = get_request_info()

    try:
        # Create new API key
        api_key, full_key = create_api_key(
            user_id=get_current_user().get("id") if get_current_user() else None,
            name=name,
            scopes=scopes,
            expires_in_days=expires_in_days,
            request_info=request_info
        )

        # Format response
        return jsonify({
            "key": api_key.to_dict(),
            "api_key": full_key  # Only returned once during creation
        }), 201

    except ValueError as e:
        return jsonify({
            "error": "Invalid parameters",
            "message": str(e)
        }), 400

    except Exception as e:
        logger.error(f"Error creating API key: {str(e)}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to create API key"
        }), 500

@api_key_bp.route('/<int:key_id>/rotate', methods=['POST'])
@login_required
@rate_limit(max_requests=5, time_window=60)
def rotate_key(key_id):
    """
    Rotate an API key by creating a new key and marking the old one as rotated
    The old key remains valid for a grace period to allow for system updates

    Response:
    {
        "key": {
            "id": 2,
            "name": "My API Key (rotated)",
            "key_prefix": "efgh5678...",
            "status": "active",
            "scopes": ["read", "write"],
            "created_at": "2023-10-03T12:00:00Z",
            "expires_at": "2023-12-31T12:00:00Z",
            "rotation_count": 1
        },
        "api_key": "efgh5678.NEW_SECRET_PART", // Only shown once
        "old_key_id": 1
    }
    """
    # Get key by ID
    api_key = APIKey.query.get_or_404(key_id)

    # Check authorization (must be owner or admin)
    if api_key.user_id != get_current_user().get("id") if get_current_user() else None and not current_user.is_administrator():
        return jsonify({
            "error": "Forbidden",
            "message": "You do not have permission to rotate this API key"
        }), 403

    # Get request info for auditing
    request_info = get_request_info()

    try:
        # Rotate the key
        new_key, full_key = rotate_api_key(
            api_key_id=key_id,
            performed_by_id=get_current_user().get("id") if get_current_user() else None,
            request_info=request_info
        )

        # Format response
        return jsonify({
            "key": new_key.to_dict(),
            "api_key": full_key,  # Only returned once during rotation
            "old_key_id": api_key.id
        })

    except APIKeyRotationError as e:
        return jsonify({
            "error": "Rotation failed",
            "message": str(e)
        }), 400

    except Exception as e:
        logger.error(f"Error rotating API key: {str(e)}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to rotate API key"
        }), 500

@api_key_bp.route('/<int:key_id>', methods=['DELETE'])
@login_required
@rate_limit(max_requests=10, time_window=60)
def revoke_key(key_id):
    """
    Revoke an API key (mark as invalid)

    Response:
    {
        "message": "API key revoked successfully",
        "key_id": 1
    }
    """
    # Get key by ID
    api_key = APIKey.query.get_or_404(key_id)

    # Check authorization (must be owner or admin)
    if api_key.user_id != get_current_user().get("id") if get_current_user() else None and not current_user.is_administrator():
        return jsonify({
            "error": "Forbidden",
            "message": "You do not have permission to revoke this API key"
        }), 403

    # Get request info for auditing
    request_info = get_request_info()

    try:
        # Revoke the key
        revoke_api_key(
            api_key_id=key_id,
            performed_by_id=get_current_user().get("id") if get_current_user() else None,
            request_info=request_info
        )

        # Format response
        return jsonify({
            "message": "API key revoked successfully",
            "key_id": key_id
        })

    except APIKeyError as e:
        return jsonify({
            "error": "Revocation failed",
            "message": str(e)
        }), 400

    except Exception as e:
        logger.error(f"Error revoking API key: {str(e)}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to revoke API key"
        }), 500

@api_key_bp.route('/<int:key_id>/events', methods=['GET'])
@login_required
@rate_limit(max_requests=20, time_window=60)
def key_events(key_id):
    """
    Get event history for an API key

    Response:
    {
        "events": [
            {
                "id": 1,
                "api_key_id": 1,
                "event_type": "created",
                "timestamp": "2023-10-03T12:00:00Z",
                "ip_address": "192.168.1.1",
                "performed_by_id": 1
            },
            {
                "id": 2,
                "api_key_id": 1,
                "event_type": "rotated",
                "timestamp": "2023-10-04T12:00:00Z",
                "ip_address": "192.168.1.1",
                "performed_by_id": 1
            }
        ]
    }
    """
    # Get key by ID
    api_key = APIKey.query.get_or_404(key_id)

    # Check authorization (must be owner or admin)
    if api_key.user_id != get_current_user().get("id") if get_current_user() else None and not current_user.is_administrator():
        return jsonify({
            "error": "Forbidden",
            "message": "You do not have permission to view events for this API key"
        }), 403

    # Get events for this key
    events = APIKeyEvent.query.filter_by(api_key_id=key_id).order_by(APIKeyEvent.timestamp.desc()).all()

    # Format response
    return jsonify({
        "events": [event.to_dict() for event in events]
    })

@api_key_bp.route('/scopes', methods=['GET'])
@rate_limit(max_requests=10, time_window=60)
def list_scopes():
    """
    List all available API key scopes

    Response:
    {
        "scopes": [
            "read",
            "write",
            "admin",
            "user",
            "system",
            "analytics",
            "billing"
        ],
        "descriptions": {
            "read": "Read-only access to API resources",
            "write": "Create, update, and delete API resources",
            "admin": "Administrative operations",
            "user": "User management operations",
            "system": "System-level operations",
            "analytics": "Access to analytics data",
            "billing": "Access to billing information"
        }
    }
    """
    # Descriptions for each scope
    scope_descriptions = {
        "read": "Read-only access to API resources",
        "write": "Create, update, and delete API resources",
        "admin": "Administrative operations",
        "user": "User management operations",
        "system": "System-level operations",
        "analytics": "Access to analytics data",
        "billing": "Access to billing information"
    }

    return jsonify({
        "scopes": AVAILABLE_SCOPES,
        "descriptions": scope_descriptions
    })

@api_key_bp.route('/verify', methods=['POST'])
@api_key_required(scopes=['read'])
def verify_key():
    """
    Verify an API key and return information about it

    Response:
    {
        "valid": true,
        "key": {
            "user_id": 1,
            "scopes": ["read", "write"],
            "status": "active",
            "expires_at": "2023-12-31T12:00:00Z"
        }
    }
    """
    # API key is already validated by the api_key_required decorator
    api_key = g.api_key

    return jsonify({
        "valid": True,
        "key": {
            "user_id": api_key.user_id,
            "scopes": json.loads(api_key.scopes) if isinstance(api_key.scopes, str) else api_key.scopes,
            "status": api_key.status,
            "expires_at": api_key.expires_at.isoformat() if api_key.expires_at else None
        }
    })

# Register API key schemas
from utils.schema_validation import register_schema, object_schema, string_schema, array_schema, number_schema

# Schema for creating an API key
register_schema("create_api_key", object_schema(
    properties={
        "name": string_schema(min_length=1, max_length=100),
        "scopes": array_schema(
            items_schema=string_schema(),
            min_items=1
        ),
        "expires_in_days": number_schema(minimum=1, maximum=365, integer_only=True)
    },
    required=["name"]
))