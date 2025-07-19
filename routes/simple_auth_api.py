"""
Simple Authentication API
"""

from flask import Blueprint, request, jsonify, session
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated
import datetime

auth_bp = Blueprint('simple_auth_api', __name__)

@auth_bp.route('/api/auth/login', methods=['POST'])
def api_login():
    """API login endpoint"""
    data = request.get_json() or {}
    
    # Check for missing credentials
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing credentials'}), 400
    
    # For demo purposes, accept any credentials
    user = get_demo_user()
    session['user'] = {
        'id': user.id,
        'name': user.name,
        'email': user.email
    }
    return jsonify({'status': 'success', 'user': session['user']})

@auth_bp.route('/api/auth/logout', methods=['POST'])
def api_logout():
    """API logout endpoint"""
    session.clear()
    return jsonify({'status': 'success'})
