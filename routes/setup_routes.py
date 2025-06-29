"""
Setup and onboarding routes
"""

from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from utils.auth_compat import login_required, current_user, get_current_user

setup_bp = Blueprint('setup', __name__)

@setup_bp.route('/setup')
def setup_main():
    """Setup wizard main page"""
    user = get_current_user()
    return render_template('setup/main.html', user=user)

@setup_bp.route('/api/setup/progress')
def setup_progress():
    """Setup progress API"""
    user = get_current_user()
    return jsonify({
        'user_id': user['id'],
        'progress': {
            'step': 1,
            'total_steps': 5,
            'completed': False
        }
    })

@setup_bp.route('/api/setup/complete', methods=['POST'])
def setup_complete():
    """Complete setup process"""
    user = get_current_user()
    return jsonify({
        'status': 'success',
        'redirect': '/dashboard'
    })