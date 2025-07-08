"""
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated
Pulse Routes
Pulse functionality for the NOUS application
"""

from flask import Blueprint, render_template, session, request, redirect, url_for, jsonify
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated

pulse_bp = Blueprint('pulse', __name__)


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

NOUS Pulse Dashboard - Unified Alert Hub
Aggregates top alerts from health, DBT, finance, shopping, and weather
"""
import logging
from flask import Blueprint, render_template, jsonify, request
from datetime import datetime

# Import core modules
from core.health import get_due_appointment_reminders, get_medications_to_refill, analyze_skill_effectiveness
from core.finance import get_budget_status, get_budget_heat_map_data
from core.shopping import get_due_shopping_lists, auto_replenish_from_expenses
from core.weather import get_weather_mood_correlation, get_weather_alerts

logger = logging.getLogger(__name__)

pulse_bp = Blueprint('pulse', __name__, url_prefix='/pulse')

@pulse_bp.route('/')
def pulse_dashboard():
    """Main pulse dashboard with all aggregated alerts"""
    try:
        # Gather all pulse data
        pulse_data = {
            'timestamp': datetime.now().isoformat(),
            'health': {
                'appointments': get_due_appointment_reminders(),
                'medications': get_medications_to_refill(),
                'dbt_analysis': analyze_skill_effectiveness()
            },
            'finance': {
                'budget_alerts': get_budget_status(),
                'heat_map': get_budget_heat_map_data()
            },
            'shopping': {
                'due_lists': get_due_shopping_lists()
            },
            'weather': {
                'mood_correlation': get_weather_mood_correlation(),
                'alerts': get_weather_alerts()
            }
        }

        # Calculate overall urgency score
        pulse_data['urgency_score'] = calculate_urgency_score(pulse_data)

        return render_template('pulse/dashboard.html', **pulse_data)

    except Exception as e:
        logger.error(f"Error loading pulse dashboard: {e}")
        return jsonify({'error': 'Failed to load pulse dashboard'}), 500

@pulse_bp.route('/api/data')
def pulse_api():
    """API endpoint for pulse data (JSON response)"""
    try:
        return jsonify({
            'health_alerts': len(get_due_appointment_reminders() + get_medications_to_refill()),
            'budget_warnings': len([b for b in get_budget_status() if b['percentage'] >= 70]),
            'shopping_due': len(get_due_shopping_lists()),
            'weather_impact': get_weather_mood_correlation().get('mood_correlation', {}).get('weather_influence', 'unknown'),
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error fetching pulse API data: {e}")
        return jsonify({'error': 'Failed to fetch pulse data'}), 500

@pulse_bp.route('/health')
def health_details():
    """Detailed health alerts view"""
    try:
        health_data = {
            'appointments': get_due_appointment_reminders(),
            'medications': get_medications_to_refill(),
            'dbt_analysis': analyze_skill_effectiveness()
        }
        return render_template('pulse/health_details.html', **health_data)
    except Exception as e:
        logger.error(f"Error loading health details: {e}")
        return jsonify({'error': 'Failed to load health details'}), 500

@pulse_bp.route('/finance')
def finance_details():
    """Detailed finance alerts view"""
    try:
        finance_data = {
            'budget_status': get_budget_status(),
            'heat_map': get_budget_heat_map_data()
        }
        return render_template('pulse/finance_details.html', **finance_data)
    except Exception as e:
        logger.error(f"Error loading finance details: {e}")
        return jsonify({'error': 'Failed to load finance details'}), 500

def calculate_urgency_score(pulse_data):
    """Calculate overall urgency score based on all alerts"""
    try:
        score = 0

        # Health urgency
        health_urgent = sum(1 for item in pulse_data['health']['appointments'] if item.get('urgency') == 'high')
        score += health_urgent * 3

        # Finance urgency
        budget_critical = sum(1 for item in pulse_data['finance']['budget_alerts'] if item.get('percentage', 0) >= 90)
        score += budget_critical * 2

        # Shopping urgency
        shopping_urgent = sum(1 for item in pulse_data['shopping']['due_lists'] if item.get('priority') == 'high')
        score += shopping_urgent * 1

        # Normalize to 0-10 scale
        return min(score, 10)

    except Exception as e:
        logger.error(f"Error calculating urgency score: {e}")
        return 0