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

Routes for Weather and Environmental Monitoring
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for

from utils.weather_helper import get_current_weather, get_weather_forecast, get_pollution_data, get_weather_alerts
from models import WeatherLocation, db

weather_bp = Blueprint('weather_routes', __name__, url_prefix='/weather')

@weather_bp.route('/')
def weather_dashboard():
    """Renders the main weather dashboard."""
    user_id = session.get('user', {}).get('id', 'demo_user')
    primary_location = WeatherLocation.query.filter_by(user_id=user_id, is_primary=True).first()
    
    if not primary_location:
        flash("Please set a primary location to view the weather dashboard.", "info")
        return redirect(url_for('weather_routes.manage_locations'))

    location_name = primary_location.name
    units = primary_location.units

    weather_data = get_current_weather(location_name, units)
    forecast_data = get_weather_forecast(location_name, 5, units)
    pollution_data = get_pollution_data(primary_location.latitude, primary_location.longitude)
    alerts = get_weather_alerts(primary_location.latitude, primary_location.longitude)

    return render_template('weather.html', 
                           weather=weather_data, 
                           forecast=forecast_data,
                           pollution=pollution_data,
                           alerts=alerts)

@weather_bp.route('/locations', methods=['GET', 'POST'])
def manage_locations():
    """Page for users to manage their saved locations."""
    user_id = session.get('user', {}).get('id', 'demo_user')
    if request.method == 'POST':
        location_name = request.form.get('location_name')
        if location_name:
            # This is a simplified add. A real implementation would get coords.
            new_loc = WeatherLocation(user_id=user_id, name=location_name, is_primary=not WeatherLocation.query.filter_by(user_id=user_id).first())
            db.session.add(new_loc)
            db.session.commit()
            flash(f"Location '{location_name}' added.", "success")
        return redirect(url_for('weather_routes.manage_locations'))

    locations = WeatherLocation.query.filter_by(user_id=user_id).all()
    return render_template('weather_locations.html', locations=locations) 