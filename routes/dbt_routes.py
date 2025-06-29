"""
DBT (Dialectical Behavior Therapy) routes
"""

from flask import Blueprint, render_template, jsonify, request
from utils.auth_compat import login_required, current_user, get_current_user

dbt_bp = Blueprint('dbt', __name__)

@dbt_bp.route('/dbt')
def dbt_main():
    """DBT main page"""
    user = get_current_user()
    return render_template('dbt/main.html', user=user)

@dbt_bp.route('/api/dbt/skills')
def dbt_skills():
    """DBT skills API"""
    return jsonify({
        'skills': [
            'Mindfulness',
            'Distress Tolerance', 
            'Emotion Regulation',
            'Interpersonal Effectiveness'
        ]
    })
