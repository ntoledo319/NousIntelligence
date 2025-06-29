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

Dashboard View Routes

This module contains view routes for the dashboard page.

@module routes.view.dashboard
@author NOUS Development Team
"""

import datetime
import logging
from flask import Blueprint, render_template, redirect, url_for, flash, session

from utils.beta_test_helper import is_beta_tester

# Create blueprint
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('', methods=['GET'])
@dashboard_bp.route('/', methods=['GET'])
def dashboard():
    """Show dashboard with data visualizations and summaries"""
    # Add comprehensive logging to diagnose the blank page issue
    try:
        user_email = session.get('user', {}).get('email if session.get('user') else 'unknown'
        user_id = session.get('user', {}).get('id', 'demo_user') if session.get('user') else 'unknown'
        logging.info(f"Dashboard accessed by user: {user_email} (ID: {user_id})")

        # Check for beta access if beta mode is enabled
        if session.get('BETA_MODE', False):
            if not is_beta_tester(user_id):
                flash("The dashboard is currently available only to beta testers.", "warning")
                return redirect(url_for('beta.request_access'))
    except Exception as e:
        logging.error(f"Error in dashboard access check: {str(e)}")
        flash("An error occurred while loading the dashboard. Please try again.", "danger")
        return redirect(url_for('index.index'))

    # Check for Google services connection
    if "google_creds" not in session:
        flash("Please connect your Google account to access all dashboard features", "warning")

    # Prepare data for the dashboard
    data = {}

    # Always include a message for first-time users
    data['first_visit'] = True

    # Create some default data to ensure template renders properly
    data['budget_categories'] = {"Groceries": 500, "Utilities": 300, "Entertainment": 200}

    # Get budget data
    try:
        from utils.budget_helper import get_budget_summary
        budget_data = get_budget_summary(session)
        if budget_data:
            data['budget_summary'] = budget_data

            # Format budget categories for the chart
            if 'categories' in budget_data:
                # Filter out categories with 0 budget
                budget_categories = {
                    cat: details['budget']
                    for cat, details in budget_data['categories'].items()
                    if details['budget'] > 0
                }
                data['budget_categories'] = budget_categories
                data['first_visit'] = False
    except Exception as e:
        logging.error(f"Error fetching budget data: {str(e)}")

    # Get trip data
    try:
        from utils.travel_helper import get_active_trip, get_upcoming_trips, get_itinerary

        active_trip = get_active_trip(session)
        if active_trip:
            # Calculate days remaining
            today = datetime.datetime.now()
            days_left = (active_trip.end_date - today).days if active_trip.end_date else 0

            # Check if it has itinerary
            itinerary = get_itinerary(active_trip.id, session)

            trip_data = active_trip.to_dict()
            trip_data['days_left'] = days_left
            trip_data['has_itinerary'] = len(itinerary) > 0
            trip_data['itinerary_count'] = len(itinerary)

            data['active_trip'] = trip_data

        upcoming_trips = get_upcoming_trips(session)
        if upcoming_trips:
            # Format upcoming trips data
            upcoming_data = []
            for trip in upcoming_trips:
                today = datetime.datetime.now()
                days_until = (trip.start_date - today).days if trip.start_date else 0

                trip_dict = trip.to_dict()
                trip_dict['days_until'] = days_until
                upcoming_data.append(trip_dict)

            data['upcoming_trips'] = upcoming_data
    except Exception as e:
        logging.error(f"Error fetching trip data: {str(e)}")

    # Get appointment data
    try:
        from utils.doctor_appointment_helper import get_upcoming_appointments
        appointments = get_upcoming_appointments(session)
        if appointments:
            data['appointments'] = appointments

        # Check medications to refill
        from utils.medication_helper import get_medications_to_refill
        medications_to_refill = get_medications_to_refill(session)
        if medications_to_refill:
            data['medications_to_refill'] = medications_to_refill
    except Exception as e:
        logging.error(f"Error fetching health data: {str(e)}")

    # Get shopping data
    try:
        from utils.shopping_helper import get_shopping_lists, get_due_shopping_lists
        from utils.product_helper import get_due_product_orders

        shopping_lists = get_shopping_lists(session)
        if shopping_lists:
            data['shopping_lists'] = shopping_lists

            # Calculate total items
            total_items = sum(len(lst.items) for lst in shopping_lists if lst.items)
            data['total_items'] = total_items

            # Get due lists
            due_lists = get_due_shopping_lists(session)
            if due_lists:
                data['due_lists'] = due_lists

            # Get products to order
            products_to_order = get_due_product_orders(session)
            if products_to_order:
                data['products_to_order'] = products_to_order
    except Exception as e:
        logging.error(f"Error fetching shopping data: {str(e)}")

    # Get pain forecast data
    try:
        from models import WeatherLocation
        from utils.weather_helper import (
            get_current_weather, get_pressure_trend, get_storm_severity,
            calculate_pain_flare_risk
        )

        user_id = session.get("user_id")

        # Try to get user's primary location
        primary_location = WeatherLocation.query.filter_by(user_id=user_id, is_primary=True).first()

        if primary_location:
            # Get weather data for pain forecast
            weather_data = get_current_weather(primary_location.name)

            if weather_data:
                # Get pressure trend data
                pressure_trend = get_pressure_trend(primary_location.name, 24)

                if pressure_trend:
                    # Get storm severity data
                    storm_data = get_storm_severity(weather_data)

                    # Calculate pain flare risk
                    pain_risk = calculate_pain_flare_risk(pressure_trend, storm_data)

                    # Prepare data for the dashboard
                    data['pain_forecast'] = {
                        'location': pressure_trend['location'],
                        'current_pressure': pressure_trend['current_pressure'],
                        'trend_direction': pressure_trend['trend_direction'],
                        'pressure_change': pressure_trend['overall_change'],
                        'risk_level': pain_risk['risk_level'],
                        'risk_score': pain_risk['risk_score'],
                        'confidence': pain_risk['confidence'],
                        'factors': pain_risk['factors'],
                        'recommendation': pain_risk['recommendation']
                    }
    except Exception as e:
        logging.error(f"Error generating pain forecast: {str(e)}")

    # Create some recent activity (could be replaced with actual activity log)
    data['recent_activity'] = [
        {
            'action': 'Added budget',
            'description': 'Created monthly budget for groceries',
            'time_ago': '2 hours ago'
        },
        {
            'action': 'Booked flight',
            'description': 'Reserved tickets for Paris trip',
            'time_ago': '1 day ago'
        },
        {
            'action': 'Added expense',
            'description': 'Recorded $45.99 for dinner',
            'time_ago': '2 days ago'
        },
        {
            'action': 'Scheduled appointment',
            'description': 'Doctor visit on June 15',
            'time_ago': '3 days ago'
        },
    ]

    return render_template("dashboard.html", **data)