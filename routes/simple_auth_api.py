"""
Simple Authentication API
"""

from flask import Blueprint, request, jsonify, session
from utils.auth_compat import get_demo_user
import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/login', methods=['POST'])
def api_login():
    """API login endpoint"""
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
