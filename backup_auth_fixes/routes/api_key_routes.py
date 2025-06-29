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

API Key Management Routes
Handles API key generation, validation, and rotation
"""

from flask import Blueprint, request, jsonify, session
import secrets
import logging

api_key_bp = Blueprint('api_key', __name__)

@api_key_bp.route('/generate', methods=['POST'])
def generate_api_key():
    """Generate a new API key for the user"""
    try:
        # Generate secure API key
        api_key = secrets.token_urlsafe(32)
        
        # In a real implementation, store this in database
        # For now, return the key for testing
        return jsonify({
            'success': True,
            'api_key': api_key,
            'message': 'API key generated successfully'
        })
    except Exception as e:
        logging.error(f"API key generation error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate API key'
        }), 500

@api_key_bp.route('/validate', methods=['POST'])
def validate_api_key():
    """Validate an API key"""
    try:
        data = request.get_json() or {}
        api_key = data.get('api_key', '')
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key required'
            }), 400
        
        # In a real implementation, check against database
        # For now, return valid for any non-empty key
        is_valid = len(api_key) >= 32
        
        return jsonify({
            'success': True,
            'valid': is_valid,
            'message': 'API key validated'
        })
    except Exception as e:
        logging.error(f"API key validation error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to validate API key'
        }), 500

@api_key_bp.route('/status', methods=['GET'])
def api_key_status():
    """Get API key status and usage"""
    try:
        return jsonify({
            'success': True,
            'status': 'active',
            'usage': {
                'requests_today': 0,
                'rate_limit': 1000,
                'remaining': 1000
            }
        })
    except Exception as e:
        logging.error(f"API key status error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get API key status'
        }), 500