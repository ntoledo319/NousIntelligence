"""

def require_authentication():
    """Check if user is authenticated, allow demo mode"""
    from flask import session, request, redirect, url_for, jsonify
    
    # Check session authentication
    if 'user' in session and session['user']:
        return None  # User is authenticated
    
    # Allow demo mode
    if request.args.get('demo') == 'true':
        return None  # Demo mode allowed
    
    # For API endpoints, return JSON error
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Authentication required', 'demo_available': True}), 401
    
    # For web routes, redirect to login
    return redirect(url_for('login'))

def get_current_user():
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

Settings API Routes

This module contains API routes for user settings management.

@module routes.api.v1.settings
@author NOUS Development Team
"""

from flask import Blueprint, request, jsonify

from models import ConversationDifficulty
from utils.security_helper import rate_limit
from utils.error_handler import APIError, validation_error
from services.settings import SettingsService

# Create blueprint with URL prefix
settings_bp = Blueprint('api_settings', __name__, url_prefix='/api/v1/settings')

# Initialize service
settings_service = SettingsService()

@settings_bp.route('', methods=['GET'])
def get_settings():
    """Get user settings"""
    try:
        # Get settings for the current user
        settings = settings_service.get_or_create_settings(session.get('user', {}).get('id', 'demo_user'))

        return jsonify({
            "success": True,
            "data": settings.to_dict()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to retrieve settings",
            "message": str(e)
        }), 500

@settings_bp.route('', methods=['PUT'])
@rate_limit(max_requests=30, time_window=60)  # 30 requests per minute
def update_settings():
    """Update user settings"""
    # Get JSON data
    data = request.get_json()
    if not data:
        raise validation_error("Missing JSON data")

    # Validate fields
    valid_fields = [
        'conversation_difficulty', 'enable_voice_responses',
        'preferred_language', 'theme', 'color_theme',
        'ai_name', 'ai_personality', 'ai_formality',
        'ai_verbosity', 'ai_enthusiasm', 'ai_emoji_usage',
        'ai_voice_type', 'ai_backstory'
    ]

    # Check for valid fields
    for field in data:
        if field not in valid_fields:
            raise validation_error(f"Invalid field: {field}")

    # Ensure conversation_difficulty is valid if provided
    if 'conversation_difficulty' in data:
        difficulty = data['conversation_difficulty']
        if difficulty not in [e.value for e in ConversationDifficulty]:
            raise validation_error(f"Invalid value for conversation_difficulty: {difficulty}")

    try:
        # Update settings using service
        settings = settings_service.update_settings(session.get('user', {}).get('id', 'demo_user'), data)

        return jsonify({
            "success": True,
            "message": "Settings updated successfully",
            "data": settings.to_dict()
        })
    except ValueError as e:
        # Handle validation errors from service
        raise validation_error(str(e))
    except Exception as e:
        # Handle other errors
        return jsonify({
            "success": False,
            "error": "Failed to update settings",
            "message": str(e)
        }), 500

@settings_bp.route('/reset', methods=['POST'])
def reset_settings():
    """Reset user settings to defaults"""
    try:
        # Reset settings using service
        settings = settings_service.reset_to_defaults(session.get('user', {}).get('id', 'demo_user'))

        if not settings:
            raise APIError("Settings not found", 404, "SETTINGS_NOT_FOUND")

        return jsonify({
            "success": True,
            "message": "Settings reset to defaults",
            "data": settings.to_dict()
        })
    except APIError:
        # Re-raise API errors
        raise
    except Exception as e:
        # Handle other errors
        return jsonify({
            "success": False,
            "error": "Failed to reset settings",
            "message": str(e)
        }), 500