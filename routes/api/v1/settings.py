"""
Settings API Routes

This module contains API routes for user settings management.

@module routes.api.v1.settings
@author NOUS Development Team
"""

from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from models import ConversationDifficulty
from utils.security_helper import rate_limit
from utils.error_handler import APIError, validation_error
from services.settings import SettingsService

# Create blueprint with URL prefix
settings_bp = Blueprint('api_settings', __name__, url_prefix='/api/v1/settings')

# Initialize service
settings_service = SettingsService()


@settings_bp.route('', methods=['GET'])
@login_required
def get_settings():
    """Get user settings"""
    try:
        # Get settings for the current user
        settings = settings_service.get_or_create_settings(current_user.id)
        
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
@login_required
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
        settings = settings_service.update_settings(current_user.id, data)
        
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
@login_required
def reset_settings():
    """Reset user settings to defaults"""
    try:
        # Reset settings using service
        settings = settings_service.reset_to_defaults(current_user.id)
        
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