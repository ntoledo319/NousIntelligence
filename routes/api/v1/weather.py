"""

from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated
def require_authentication():
    """Check if user is authenticated, allow demo mode"""
    from flask import session, request, redirect, url_for, jsonify
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated
    
    # Check session authentication
    if 'user' in session and session['user']:
        return None  # User is authenticated
    
    # Allow demo mode
    if request.args.get('demo') == 'true':
        return None  # Demo mode allowed
    
    # For API endpoints, return JSON error
    if request.path.startswith('/api/'):
        return jsonify({'error': "Demo mode - limited access", 'demo_available': True}), 401
    
    # For web routes, redirect to login
    return redirect(url_for("main.demo"))

def get_get_demo_user()():
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

Weather API Routes

This module contains API routes for weather data and location management.

@module routes.api.v1.weather
@author NOUS Development Team
"""

from flask import Blueprint, request, jsonify

from utils.security_helper import rate_limit
from utils.error_handler import APIError, validation_error
from utils.weather_helper import (
    get_current_weather, get_weather_forecast, get_location_coordinates,
    format_weather_output, format_forecast_output, get_pressure_trend,
    calculate_pain_flare_risk, get_storm_severity, format_pain_forecast_output
)
from models import db, WeatherLocation

# Create blueprint with URL prefix
weather_bp = Blueprint('api_weather', __name__, url_prefix='/api/v1/weather')

@weather_bp.route('/current', methods=['GET'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def api_get_current_weather():
    """Get current weather for a location"""
    location = request.args.get("location", "")
    units = request.args.get("units", "imperial")

    if not location:
        return jsonify({"error": "Location is required"}), 400

    # Get weather data
    weather_data = get_current_weather(location, units)

    if not weather_data or "error" in weather_data:
        return jsonify({"error": "Failed to retrieve weather data", "details": weather_data.get("error") if weather_data else None}), 500

    # Format the output
    formatted_data = format_weather_output(weather_data)

    return jsonify({
        "success": True,
        "data": formatted_data
    })

@weather_bp.route('/forecast', methods=['GET'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def api_get_weather_forecast():
    """Get weather forecast for a location"""
    location = request.args.get("location", "")
    days = int(request.args.get("days", 5))
    units = request.args.get("units", "imperial")

    if not location:
        return jsonify({"error": "Location is required"}), 400

    # Limit to reasonable range
    if days < 1:
        days = 1
    elif days > 10:
        days = 10

    # Get forecast data
    forecast_data = get_weather_forecast(location, days, units)

    if not forecast_data or "error" in forecast_data:
        return jsonify({"error": "Failed to retrieve forecast data", "details": forecast_data.get("error") if forecast_data else None}), 500

    # Format the output
    formatted_data = format_forecast_output(forecast_data)

    return jsonify({
        "success": True,
        "data": formatted_data
    })

@weather_bp.route('/locations', methods=['GET'])
def api_get_weather_locations():
    """Get saved weather locations for the user"""
    user_id = session.get('user', {}).get('id', 'demo_user')

    # Query locations for this user
    locations = WeatherLocation.query.filter_by(user_id=user_id).all()

    # Format the output
    data = [location.to_dict() for location in locations]

    return jsonify({
        "success": True,
        "data": data
    })

@weather_bp.route('/locations', methods=['POST'])
@rate_limit(max_requests=10, time_window=60)  # 10 requests per minute
def api_add_weather_location():
    """Add a new weather location for the user"""
    data = request.get_json()

    # Validate required fields
    if not data:
        return jsonify({"error": "No data provided"}), 400

    location_name = data.get("name", "").strip()

    if not location_name:
        return jsonify({"error": "Location name is required"}), 400

    user_id = session.get('user', {}).get('id', 'demo_user')

    # Check if we have coordinates
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    # If not, get them from the location name
    if not latitude or not longitude:
        coords = get_location_coordinates(location_name)
        if not coords:
            return jsonify({"error": f"Could not find coordinates for '{location_name}'"}), 400

        latitude = coords["latitude"]
        longitude = coords["longitude"]
        display_name = coords.get("display_name", location_name)
    else:
        display_name = data.get("display_name", location_name)

    # Check if this is the first location for the user
    is_first = WeatherLocation.query.filter_by(user_id=user_id).count() == 0

    # Create the location
    new_location = WeatherLocation(
        name=location_name,
        display_name=display_name,
        latitude=latitude,
        longitude=longitude,
        is_primary=data.get("is_primary", is_first),
        units=data.get("units", "imperial"),
        user_id=user_id
    )

    db.session.add(new_location)

    # If this is the primary location, make sure all others are not primary
    if new_location.is_primary:
        WeatherLocation.query.filter(
            WeatherLocation.user_id == user_id,
            WeatherLocation.id != new_location.id
        ).update({"is_primary": False})

    db.session.commit()

    return jsonify({
        "success": True,
        "message": f"Added location '{location_name}'",
        "data": new_location.to_dict()
    })

@weather_bp.route('/locations/<int:location_id>', methods=['DELETE'])
def api_delete_weather_location(location_id):
    """Delete a weather location"""
    user_id = session.get('user', {}).get('id', 'demo_user')

    # Find the location
    location = WeatherLocation.query.filter_by(id=location_id, user_id=user_id).first()

    if not location:
        return jsonify({"error": "Location not found"}), 404

    # Check if it's the primary location
    was_primary = location.is_primary

    # Delete the location
    db.session.delete(location)

    # If it was primary, set another as primary if available
    if was_primary:
        next_location = WeatherLocation.query.filter_by(user_id=user_id).first()
        if next_location:
            next_location.is_primary = True

    db.session.commit()

    return jsonify({
        "success": True,
        "message": f"Deleted location '{location.name}'"
    })

@weather_bp.route('/locations/<int:location_id>/primary', methods=['PUT'])
def api_set_primary_weather_location(location_id):
    """Set a location as the primary location"""
    user_id = session.get('user', {}).get('id', 'demo_user')

    # Find the location
    location = WeatherLocation.query.filter_by(id=location_id, user_id=user_id).first()

    if not location:
        return jsonify({"error": "Location not found"}), 404

    # Set this as primary
    location.is_primary = True

    # Set all others as not primary
    WeatherLocation.query.filter(
        WeatherLocation.user_id == user_id,
        WeatherLocation.id != location_id
    ).update({"is_primary": False})

    db.session.commit()

    return jsonify({
        "success": True,
        "message": f"Set '{location.name}' as primary location",
        "data": location.to_dict()
    })

@weather_bp.route('/pain-forecast', methods=['GET'])
def api_pain_flare_forecast():
    """Get pain flare forecast based on weather conditions"""
    user_id = session.get('user', {}).get('id', 'demo_user')

    # Get location from query or use primary location
    location_id = request.args.get("location_id")

    if location_id:
        # Find specific location
        location = WeatherLocation.query.filter_by(id=location_id, user_id=user_id).first()
    else:
        # Find primary location
        location = WeatherLocation.query.filter_by(user_id=user_id, is_primary=True).first()

    if not location:
        return jsonify({"error": "No location found. Please add a location first."}), 404

    # Get weather data
    weather_data = get_current_weather(location.name)

    if not weather_data:
        return jsonify({"error": "Failed to retrieve weather data"}), 500

    # Get pressure trend data
    pressure_trend = get_pressure_trend(location.name, 24)

    if not pressure_trend:
        return jsonify({"error": "Failed to retrieve pressure trend data"}), 500

    # Get storm severity data
    storm_data = get_storm_severity(weather_data)

    # Calculate pain flare risk
    pain_risk = calculate_pain_flare_risk(pressure_trend, storm_data)

    # Format the output
    formatted_data = format_pain_forecast_output(pain_risk, pressure_trend, location)

    return jsonify({
        "success": True,
        "data": formatted_data
    })