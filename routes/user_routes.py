"""
User management routes
"""

from flask import Blueprint, render_template, jsonify, request
from utils.auth_compat import login_required, get_demo_user, is_authenticated

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile')
def profile():
    """User profile page"""
    user = get_demo_user()()
    return render_template('profile.html', user=user)

@user_bp.route('/api/user/profile')
def api_profile():
    """User profile API"""
    user = get_demo_user()()
    return jsonify(user)
