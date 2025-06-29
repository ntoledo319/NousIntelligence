"""

def require_authentication():
    """Check if user is authenticated, allow demo mode"""
    from flask import session, request, redirect, url_for, jsonify
    
    # Check session authentication
    if 'user' in session and session['user']:
        return None  # User is authenticated
    
    # Allow demo mode
    if request.args.get('demo') == 'true':
        return None  # Demo mode allowed
    
    # For API endpoints, return JSON error
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Authentication required', 'demo_available': True}), 401
    
    # For web routes, redirect to login
    return redirect(url_for('login'))

def get_current_user():
    """Get current user from session with demo fallback"""
    from flask import session
    return session.get('user', {
        'id': 'demo_user',
        'name': 'Demo User',
        'email': 'demo@example.com',
        'is_demo': True
    })

def is_authenticated():
    """Check if user is authenticated"""
    from flask import session
    return 'user' in session and session['user'] is not None

Routes for Location and Navigation Services
"""
from flask import Blueprint, render_template, request, jsonify
from utils.maps_helper import get_directions, search_places

maps_bp = Blueprint('maps_routes', __name__, url_prefix='/maps')

@maps_bp.route('/')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def maps_page():
    """Renders the main maps and navigation page."""
    return render_template('maps.html')

@maps_bp.route('/directions', methods=['POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def get_directions_route():
    """Gets directions between two locations."""
    data = request.get_json()
    origin = data.get('origin')
    destination = data.get('destination')
    mode = data.get('mode', 'driving')

    if not origin or not destination:
        return jsonify({"success": False, "error": "Origin and destination are required."}), 400

    directions = get_directions(origin, destination, mode)
    return jsonify(directions)

@maps_bp.route('/search_places', methods=['POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def search_places_route():
    """Searches for places near a location."""
    data = request.get_json()
    query = data.get('query')
    location = data.get('location') # e.g., "40.7128,-74.0060"

    if not query:
        return jsonify({"success": False, "error": "A search query is required."}), 400

    places = search_places(query, location=location)
    return jsonify(places) 