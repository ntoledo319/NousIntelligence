"""
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated
Onboarding Routes Routes
Onboarding Routes functionality for the NOUS application
"""

from flask import Blueprint, render_template, session, request, redirect, url_for, jsonify
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated

onboarding_routes_bp = Blueprint('onboarding_routes', __name__)


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

Onboarding Routes - User Onboarding and Setup Experience
Guided setup, preferences collection, feature introduction, and account configuration
"""

import logging
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from typing import Dict, Any, List, Optional
import json

logger = logging.getLogger(__name__)

# Create blueprint
onboarding_bp = Blueprint('onboarding', __name__, url_prefix='/onboarding')

# Onboarding steps configuration
ONBOARDING_STEPS = [
    {
        'id': 'welcome',
        'title': 'Welcome to NOUS',
        'description': 'Your AI-powered personal assistant',
        'component': 'welcome',
        'required': True,
        'estimated_time': 1
    },
    {
        'id': 'profile_setup',
        'title': 'Complete Your Profile',
        'description': 'Tell us about yourself to personalize your experience',
        'component': 'profile_form',
        'required': True,
        'estimated_time': 3
    },
    {
        'id': 'preferences',
        'title': 'Set Your Preferences',
        'description': 'Configure how NOUS works best for you',
        'component': 'preferences_form',
        'required': True,
        'estimated_time': 2
    },
    {
        'id': 'integrations',
        'title': 'Connect Your Accounts',
        'description': 'Link your Google, Spotify, and other accounts',
        'component': 'integrations_setup',
        'required': False,
        'estimated_time': 5
    },
    {
        'id': 'goals_setup',
        'title': 'Set Your Goals',
        'description': 'Define what you want to achieve with NOUS',
        'component': 'goals_form',
        'required': False,
        'estimated_time': 3
    },
    {
        'id': 'feature_tour',
        'title': 'Feature Tour',
        'description': 'Discover what NOUS can do for you',
        'component': 'feature_tour',
        'required': False,
        'estimated_time': 4
    },
    {
        'id': 'completion',
        'title': 'You\'re All Set!',
        'description': 'Welcome to your personalized NOUS experience',
        'component': 'completion',
        'required': True,
        'estimated_time': 1
    }
]

# Sample preference options
PREFERENCE_OPTIONS = {
    'communication_style': [
        {'value': 'casual', 'label': 'Casual and friendly'},
        {'value': 'professional', 'label': 'Professional and formal'},
        {'value': 'concise', 'label': 'Brief and to the point'},
        {'value': 'detailed', 'label': 'Detailed explanations'}
    ],
    'notification_frequency': [
        {'value': 'high', 'label': 'All notifications'},
        {'value': 'medium', 'label': 'Important notifications only'},
        {'value': 'low', 'label': 'Critical notifications only'},
        {'value': 'none', 'label': 'No notifications'}
    ],
    'ai_assistance_level': [
        {'value': 'proactive', 'label': 'Proactive suggestions'},
        {'value': 'responsive', 'label': 'Respond when asked'},
        {'value': 'minimal', 'label': 'Minimal assistance'}
    ],
    'data_privacy': [
        {'value': 'full', 'label': 'Full personalization (recommended)'},
        {'value': 'limited', 'label': 'Limited data usage'},
        {'value': 'minimal', 'label': 'Minimal data collection'}
    ]
}

# Sample goal categories
GOAL_CATEGORIES = [
    {
        'id': 'productivity',
        'name': 'Productivity',
        'icon': '📈',
        'description': 'Manage tasks, schedule, and workflow',
        'templates': [
            'Complete daily task list',
            'Improve time management',
            'Reduce meeting overhead'
        ]
    },
    {
        'id': 'health',
        'name': 'Health & Wellness',
        'icon': '🏃',
        'description': 'Track fitness, nutrition, and wellbeing',
        'templates': [
            'Exercise 30 minutes daily',
            'Drink 8 glasses of water',
            'Get 8 hours of sleep'
        ]
    },
    {
        'id': 'learning',
        'name': 'Learning',
        'icon': '📚',
        'description': 'Acquire new skills and knowledge',
        'templates': [
            'Learn a new language',
            'Read 20 books this year',
            'Complete online course'
        ]
    },
    {
        'id': 'financial',
        'name': 'Financial',
        'icon': '💰',
        'description': 'Manage money and investments',
        'templates': [
            'Save $1000 this month',
            'Create emergency fund',
            'Track daily expenses'
        ]
    },
    {
        'id': 'relationships',
        'name': 'Relationships',
        'icon': '👥',
        'description': 'Strengthen connections with others',
        'templates': [
            'Call family weekly',
            'Schedule regular date nights',
            'Meet new people'
        ]
    }
]

@onboarding_bp.route('/')
def onboarding_start():
    """Start the onboarding process"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for("main.demo"))
        
        # Check if user has already completed onboarding
        if session.get('onboarding_completed'):
            return redirect(url_for('main.dashboard'))
        
        # Initialize onboarding session
        session['onboarding_step'] = 0
        session['onboarding_data'] = {}
        
        return render_template('onboarding/start.html', 
                             steps=ONBOARDING_STEPS,
                             total_time=sum(step['estimated_time'] for step in ONBOARDING_STEPS))
    
    except Exception as e:
        logger.error(f"Error starting onboarding: {str(e)}")
        return render_template('error.html', error="Failed to start onboarding"), 500

@onboarding_bp.route('/step/<int:step_index>')
def onboarding_step(step_index):
    """Display specific onboarding step"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for("main.demo"))
        
        # Validate step index
        if step_index < 0 or step_index >= len(ONBOARDING_STEPS):
            return redirect(url_for('onboarding.onboarding_start'))
        
        current_step = ONBOARDING_STEPS[step_index]
        session['onboarding_step'] = step_index
        
        # Get template based on step component
        template_map = {
            'welcome': 'onboarding/welcome.html',
            'profile_form': 'onboarding/profile_setup.html',
            'preferences_form': 'onboarding/preferences.html',
            'integrations_setup': 'onboarding/integrations.html',
            'goals_form': 'onboarding/goals.html',
            'feature_tour': 'onboarding/feature_tour.html',
            'completion': 'onboarding/completion.html'
        }
        
        template = template_map.get(current_step['component'], 'onboarding/generic_step.html')
        
        return render_template(template,
                             step=current_step,
                             step_index=step_index,
                             total_steps=len(ONBOARDING_STEPS),
                             progress=(step_index + 1) / len(ONBOARDING_STEPS) * 100,
                             preference_options=PREFERENCE_OPTIONS,
                             goal_categories=GOAL_CATEGORIES,
                             onboarding_data=session.get('onboarding_data', {}))
    
    except Exception as e:
        logger.error(f"Error displaying onboarding step: {str(e)}")
        return render_template('error.html', error="Failed to load onboarding step"), 500

@onboarding_bp.route('/api/step/<int:step_index>', methods=['POST'])
def save_onboarding_step(step_index):
    """Save data from onboarding step"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': "Demo mode - limited access"}), 401
        
        data = request.get_json()
        
        # Validate step index
        if step_index < 0 or step_index >= len(ONBOARDING_STEPS):
            return jsonify({'error': 'Invalid step'}), 400
        
        current_step = ONBOARDING_STEPS[step_index]
        
        # Initialize onboarding data if not exists
        if 'onboarding_data' not in session:
            session['onboarding_data'] = {}
        
        # Save step data
        session['onboarding_data'][current_step['id']] = data
        session['onboarding_step'] = step_index
        
        # Process specific steps
        if current_step['id'] == 'profile_setup':
            # Validate profile data
            required_fields = ['first_name', 'last_name', 'timezone']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'{field} is required'}), 400
        
        elif current_step['id'] == 'preferences':
            # Save preferences to user session
            session['user_preferences'] = data
        
        elif current_step['id'] == 'goals_setup':
            # Process goals data
            goals = data.get('goals', [])
            session['user_goals'] = goals
        
        # Determine next step
        next_step_index = step_index + 1
        if next_step_index >= len(ONBOARDING_STEPS):
            # Onboarding complete
            session['onboarding_completed'] = True
            return jsonify({
                'success': True,
                'next_step': None,
                'completed': True,
                'redirect_url': url_for('main.dashboard')
            })
        
        return jsonify({
            'success': True,
            'next_step': next_step_index,
            'completed': False,
            'next_url': url_for('onboarding.onboarding_step', step_index=next_step_index)
        })
    
    except Exception as e:
        logger.error(f"Error saving onboarding step: {str(e)}")
        return jsonify({'error': 'Failed to save step data'}), 500

@onboarding_bp.route('/api/skip-step/<int:step_index>', methods=['POST'])
def skip_onboarding_step(step_index):
    """Skip an optional onboarding step"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': "Demo mode - limited access"}), 401
        
        # Validate step index
        if step_index < 0 or step_index >= len(ONBOARDING_STEPS):
            return jsonify({'error': 'Invalid step'}), 400
        
        current_step = ONBOARDING_STEPS[step_index]
        
        # Check if step can be skipped
        if current_step['required']:
            return jsonify({'error': 'This step is required and cannot be skipped'}), 400
        
        # Mark step as skipped
        if 'onboarding_data' not in session:
            session['onboarding_data'] = {}
        
        session['onboarding_data'][current_step['id']] = {'skipped': True}
        
        # Move to next step
        next_step_index = step_index + 1
        if next_step_index >= len(ONBOARDING_STEPS):
            session['onboarding_completed'] = True
            return jsonify({
                'success': True,
                'next_step': None,
                'completed': True,
                'redirect_url': url_for('main.dashboard')
            })
        
        return jsonify({
            'success': True,
            'next_step': next_step_index,
            'next_url': url_for('onboarding.onboarding_step', step_index=next_step_index)
        })
    
    except Exception as e:
        logger.error(f"Error skipping onboarding step: {str(e)}")
        return jsonify({'error': 'Failed to skip step'}), 500

@onboarding_bp.route('/api/progress')
def get_onboarding_progress():
    """Get current onboarding progress"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': "Demo mode - limited access"}), 401
        
        current_step = session.get('onboarding_step', 0)
        onboarding_data = session.get('onboarding_data', {})
        completed = session.get('onboarding_completed', False)
        
        # Calculate completion percentage
        completed_steps = len([step for step in ONBOARDING_STEPS 
                              if step['id'] in onboarding_data])
        progress_percentage = (completed_steps / len(ONBOARDING_STEPS)) * 100
        
        return jsonify({
            'success': True,
            'current_step': current_step,
            'total_steps': len(ONBOARDING_STEPS),
            'progress_percentage': progress_percentage,
            'completed': completed,
            'onboarding_data': onboarding_data
        })
    
    except Exception as e:
        logger.error(f"Error getting onboarding progress: {str(e)}")
        return jsonify({'error': 'Failed to get progress'}), 500

@onboarding_bp.route('/api/complete', methods=['POST'])
def complete_onboarding():
    """Complete the onboarding process"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': "Demo mode - limited access"}), 401
        
        onboarding_data = session.get('onboarding_data', {})
        
        # Process and save all onboarding data
        user_profile = {}
        user_preferences = {}
        user_goals = []
        
        # Extract profile data
        if 'profile_setup' in onboarding_data:
            profile_data = onboarding_data['profile_setup']
            user_profile = {
                'first_name': profile_data.get('first_name'),
                'last_name': profile_data.get('last_name'),
                'timezone': profile_data.get('timezone'),
                'bio': profile_data.get('bio'),
                'interests': profile_data.get('interests', [])
            }
        
        # Extract preferences
        if 'preferences' in onboarding_data:
            user_preferences = onboarding_data['preferences']
        
        # Extract goals
        if 'goals_setup' in onboarding_data:
            user_goals = onboarding_data['goals_setup'].get('goals', [])
        
        # Mark onboarding as completed
        session['onboarding_completed'] = True
        session['user_profile'] = user_profile
        session['user_preferences'] = user_preferences
        session['user_goals'] = user_goals
        
        # Log completion
        logger.info(f"User {user_id} completed onboarding")
        
        return jsonify({
            'success': True,
            'message': 'Onboarding completed successfully',
            'redirect_url': url_for('main.dashboard'),
            'profile': user_profile,
            'preferences': user_preferences,
            'goals_count': len(user_goals)
        })
    
    except Exception as e:
        logger.error(f"Error completing onboarding: {str(e)}")
        return jsonify({'error': 'Failed to complete onboarding'}), 500

@onboarding_bp.route('/api/restart', methods=['POST'])
def restart_onboarding():
    """Restart the onboarding process"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': "Demo mode - limited access"}), 401
        
        # Clear onboarding data
        session.pop('onboarding_completed', None)
        session.pop('onboarding_step', None)
        session.pop('onboarding_data', None)
        
        return jsonify({
            'success': True,
            'message': 'Onboarding restarted',
            'redirect_url': url_for('onboarding.onboarding_start')
        })
    
    except Exception as e:
        logger.error(f"Error restarting onboarding: {str(e)}")
        return jsonify({'error': 'Failed to restart onboarding'}), 500

@onboarding_bp.route('/welcome')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def welcome_page():
    """Welcome page for new users"""
    return render_template('onboarding/welcome_standalone.html', steps=ONBOARDING_STEPS)

@onboarding_bp.route('/checklist')
def onboarding_checklist():
    """Onboarding checklist for existing users"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for("main.demo"))
    
    onboarding_data = session.get('onboarding_data', {})
    
    # Calculate completion status for each step
    step_status = []
    for step in ONBOARDING_STEPS:
        status = {
            'step': step,
            'completed': step['id'] in onboarding_data,
            'skipped': onboarding_data.get(step['id'], {}).get('skipped', False)
        }
        step_status.append(status)
    
    return render_template('onboarding/checklist.html', 
                         step_status=step_status,
                         total_steps=len(ONBOARDING_STEPS))

# Error handlers
@onboarding_bp.errorhandler(404)
def onboarding_not_found(error):
    return render_template('onboarding/404.html'), 404

@onboarding_bp.errorhandler(500)
def onboarding_server_error(error):
    return render_template('onboarding/500.html'), 500

# Utility functions
def get_onboarding_statistics():
    """Get onboarding completion statistics (for admin use)"""
    # This would normally query the database
    # For now, return sample statistics
    return {
        'total_users': 1250,
        'completed_onboarding': 987,
        'completion_rate': 78.96,
        'average_completion_time': 18.5,  # minutes
        'most_skipped_step': 'integrations',
        'drop_off_points': ['preferences', 'goals_setup']
    }

def generate_onboarding_insights():
    """Generate insights about the onboarding process"""
    return [
        {
            'type': 'info',
            'message': 'Most users complete onboarding in under 20 minutes',
            'action': 'Consider your goals and preferences carefully'
        },
        {
            'type': 'tip',
            'message': 'Connecting integrations now saves time later',
            'action': 'Link your most-used accounts during setup'
        },
        {
            'type': 'success',
            'message': 'Users who complete onboarding are 3x more active',
            'action': 'Complete all steps for the best experience'
        }
    ]

def validate_onboarding_data(step_id, data):
    """Validate onboarding step data"""
    validation_rules = {
        'profile_setup': {
            'required': ['first_name', 'last_name', 'timezone'],
            'optional': ['bio', 'interests']
        },
        'preferences': {
            'required': ['communication_style', 'notification_frequency'],
            'optional': ['ai_assistance_level', 'data_privacy']
        },
        'goals_setup': {
            'required': [],
            'optional': ['goals']
        }
    }
    
    rules = validation_rules.get(step_id, {})
    errors = []
    
    # Check required fields
    for field in rules.get('required', []):
        if not data.get(field):
            errors.append(f'{field} is required')
    
    # Validate specific fields
    if step_id == 'preferences':
        valid_styles = [opt['value'] for opt in PREFERENCE_OPTIONS['communication_style']]
        if data.get('communication_style') not in valid_styles:
            errors.append('Invalid communication style')
    
    return errors