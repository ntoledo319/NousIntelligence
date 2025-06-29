"""
Weather information routes
"""

from flask import Blueprint, render_template, jsonify, request
from utils.auth_compat import login_required, get_demo_user, is_authenticated

weather_bp = Blueprint('weather', __name__)

@weather_bp.route('/weather')
def weather_main():
    """Weather main page"""
    user = get_demo_user()()
    return render_template('weather/main.html', user=user)

@weather_bp.route('/api/weather/current')
def weather_current():
    """Current weather API"""
    return jsonify({
        'weather': 'Sunny',
        'temperature': '72°F',
        'location': 'Demo City'
    })
