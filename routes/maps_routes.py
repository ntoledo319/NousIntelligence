"""
Maps and location routes
"""

from flask import Blueprint, render_template, jsonify, request
from utils.auth_compat import login_required, get_demo_user, is_authenticated

maps_bp = Blueprint('maps', __name__)

@maps_bp.route('/maps')
def maps_main():
    """Maps main page"""
    user = get_demo_user()
    return render_template('maps/main.html', user=user)

@maps_bp.route('/api/maps/location')
def maps_location():
    """Location API"""
    return jsonify({
        'location': 'Demo Location',
        'coordinates': [0, 0]
    })
