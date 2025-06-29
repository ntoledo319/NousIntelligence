"""
CBT (Cognitive Behavioral Therapy) routes
"""

from flask import Blueprint, render_template, jsonify, request
from utils.auth_compat import login_required, current_user, get_current_user

cbt_bp = Blueprint('cbt', __name__)

@cbt_bp.route('/cbt')
def cbt_main():
    """CBT main page"""
    user = get_current_user()
    return render_template('cbt/main.html', user=user)

@cbt_bp.route('/api/cbt/exercises')
def cbt_exercises():
    """CBT exercises API"""
    return jsonify({
        'exercises': [
            'Thought Records',
            'Behavioral Experiments',
            'Mood Tracking',
            'Cognitive Restructuring'
        ]
    })
