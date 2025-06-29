"""
Recovery and support routes
"""

from flask import Blueprint, render_template, jsonify, request
from utils.auth_compat import login_required, current_user, get_current_user

recovery_bp = Blueprint('recovery', __name__)

@recovery_bp.route('/recovery')
def recovery_main():
    """Recovery support main page"""
    user = get_current_user()
    return render_template('recovery/main.html', user=user)

@recovery_bp.route('/api/recovery/resources')
def recovery_resources():
    """Recovery resources API"""
    return jsonify({
        'resources': [
            {'name': 'AA Resources', 'type': 'alcoholism'},
            {'name': 'DBT Skills', 'type': 'mental_health'},
            {'name': 'CBT Exercises', 'type': 'therapy'},
            {'name': 'Crisis Support', 'type': 'emergency'}
        ]
    })