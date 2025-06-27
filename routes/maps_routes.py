"""
Routes for Location and Navigation Services
"""
from flask import Blueprint, render_template, request, jsonify
from utils.maps_helper import get_directions, search_places

maps_bp = Blueprint('maps_routes', __name__, url_prefix='/maps')

@maps_bp.route('/')
def maps_page():
    """Renders the main maps and navigation page."""
    return render_template('maps.html')

@maps_bp.route('/directions', methods=['POST'])
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
def search_places_route():
    """Searches for places near a location."""
    data = request.get_json()
    query = data.get('query')
    location = data.get('location') # e.g., "40.7128,-74.0060"

    if not query:
        return jsonify({"success": False, "error": "A search query is required."}), 400

    places = search_places(query, location=location)
    return jsonify(places) 