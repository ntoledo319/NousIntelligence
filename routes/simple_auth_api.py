"""
Simple Authentication API
"""

from flask import Blueprint, request, jsonify, session
from utils.auth_compat import login_required, get_demo_user, is_authenticated
import jwt
import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/login', methods=['POST'])
def api_login():
    """API login endpoint"""
    user_data = {
        'id': 'api_user',
        'name': 'API User',
        'email': 'api@nous.app'
    }
    session['user'] = user_data
    return jsonify({'status': 'success', 'user': user_data})

@auth_bp.route('/api/auth/logout', methods=['POST'])
def api_logout():
    """API logout endpoint"""
    session.clear()
    return jsonify({'status': 'success'})

def validate_api_token(token):
    """Validate API token"""
    # Simple validation for now
    return {'valid': True} if token else None
