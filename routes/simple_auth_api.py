"""
Simple Authentication API
Provides basic authentication endpoints without complex JWT dependencies
"""

import logging
import secrets
import hashlib
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash

logger = logging.getLogger(__name__)

# Create blueprint with proper export name
auth_bp = Blueprint('auth_api', __name__, url_prefix='/api/auth')

# Simple in-memory token storage (use database in production)
_api_tokens = {}

def generate_api_token(user_id: str) -> str:
    """Generate simple API token"""
    token_data = f"{user_id}_{datetime.now().isoformat()}_{secrets.token_urlsafe(16)}"
    token = hashlib.sha256(token_data.encode()).hexdigest()
    
    # Store token with expiry (24 hours)
    _api_tokens[token] = {
        'user_id': user_id,
        'expires_at': datetime.now() + timedelta(hours=24),
        'created_at': datetime.now()
    }
    
    return token

def validate_api_token(token: str) -> dict:
    """Validate API token and return user info"""
    if not token or token not in _api_tokens:
        return None
    
    token_data = _api_tokens[token]
    
    # Check if expired
    if datetime.now() > token_data['expires_at']:
        del _api_tokens[token]
        return None
    
    return token_data

def require_auth(allow_demo=False):
    """Decorator for routes that require authentication"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            # Check session authentication first
            if 'user' in session and session['user']:
                return f(*args, **kwargs)
            
            # Check API token authentication
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                token_data = validate_api_token(token)
                if token_data:
                    # Add user info to request context
                    request.auth_user_id = token_data['user_id']
                    return f(*args, **kwargs)
            
            # Allow demo mode if specified
            if allow_demo and request.args.get('demo') == 'true':
                request.auth_user_id = 'demo_user'
                return f(*args, **kwargs)
            
            return jsonify({'error': 'Authentication required'}), 401
        
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

@auth_bp.route('/status', methods=['GET'])
def auth_status():
    """Check authentication status"""
    # Check session
    if 'user' in session and session['user']:
        return jsonify({
            'authenticated': True,
            'method': 'session',
            'user': session['user']
        })
    
    # Check API token
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        token_data = validate_api_token(token)
        if token_data:
            return jsonify({
                'authenticated': True,
                'method': 'token',
                'user_id': token_data['user_id'],
                'expires_at': token_data['expires_at'].isoformat()
            })
    
    return jsonify({
        'authenticated': False,
        'demo_available': True
    })

@auth_bp.route('/demo-token', methods=['POST'])
def demo_token():
    """Generate demo API token for testing"""
    token = generate_api_token('demo_user_123')
    
    return jsonify({
        'access_token': token,
        'token_type': 'Bearer',
        'expires_in': 86400,  # 24 hours
        'user_id': 'demo_user_123',
        'demo': True
    })

@auth_bp.route('/session-login', methods=['POST'])
def session_login():
    """Login using session (existing Google OAuth flow)"""
    if 'user' not in session:
        return jsonify({
            'error': 'No active session. Please login via Google OAuth first.',
            'login_url': '/login'
        }), 401
    
    # Generate API token for session user
    user = session['user']
    token = generate_api_token(user['id'])
    
    return jsonify({
        'access_token': token,
        'token_type': 'Bearer',
        'expires_in': 86400,
        'user': user
    })

@auth_bp.route('/revoke', methods=['POST'])
@require_auth()
def revoke_token():
    """Revoke current API token"""
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        if token in _api_tokens:
            del _api_tokens[token]
            return jsonify({'message': 'Token revoked successfully'})
    
    return jsonify({'message': 'No token to revoke'})

@auth_bp.route('/tokens', methods=['GET'])
@require_auth()
def list_tokens():
    """List active tokens for current user"""
    user_id = getattr(request, 'auth_user_id', session.get('user', {}).get('id'))
    if not user_id:
        return jsonify({'error': 'User ID not found'}), 400
    
    user_tokens = []
    for token, data in _api_tokens.items():
        if data['user_id'] == user_id:
            user_tokens.append({
                'token': token[:8] + '...',  # Masked token
                'created_at': data['created_at'].isoformat(),
                'expires_at': data['expires_at'].isoformat()
            })
    
    return jsonify({
        'tokens': user_tokens,
        'total': len(user_tokens)
    })

# Health check for auth system
@auth_bp.route('/health', methods=['GET'])
def auth_health():
    """Authentication system health check"""
    return jsonify({
        'status': 'healthy',
        'active_tokens': len(_api_tokens),
        'session_auth': 'user' in session,
        'timestamp': datetime.now().isoformat()
    })

# Export the blueprint
__all__ = ['auth_bp', 'require_auth', 'validate_api_token']