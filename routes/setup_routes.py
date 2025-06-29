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

Setup Wizard Routes

Complete setup wizard for new users after first login.
Optimized flow with beautiful design and comprehensive preferences.
"""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, session
from services.setup_service import setup_service
from utils.multilingual_voice import LANGUAGE_CODES

logger = logging.getLogger(__name__)

# Create blueprint
setup_bp = Blueprint('setup', __name__, url_prefix='/setup')

def get_user_id():
    """Get current user ID from session"""
    if 'user' in session and session['user']:
        return str(session['user']['id'])
    return None

def is_authenticated():
    """Check if user is authenticated via session"""
    return 'user' in session and session['user'] is not None

# Configuration data for forms
LANGUAGE_OPTIONS = [
    {'code': 'en-US', 'name': 'English (US)', 'flag': '🇺🇸'},
    {'code': 'en-GB', 'name': 'English (UK)', 'flag': '🇬🇧'},
    {'code': 'es-ES', 'name': 'Spanish (Spain)', 'flag': '🇪🇸'},
    {'code': 'es-MX', 'name': 'Spanish (Mexico)', 'flag': '🇲🇽'},
    {'code': 'fr-FR', 'name': 'French', 'flag': '🇫🇷'},
    {'code': 'de-DE', 'name': 'German', 'flag': '🇩🇪'},
    {'code': 'it-IT', 'name': 'Italian', 'flag': '🇮🇹'},
    {'code': 'ja-JP', 'name': 'Japanese', 'flag': '🇯🇵'},
    {'code': 'ko-KR', 'name': 'Korean', 'flag': '🇰🇷'},
    {'code': 'zh-CN', 'name': 'Chinese (Simplified)', 'flag': '🇨🇳'},
    {'code': 'zh-TW', 'name': 'Chinese (Traditional)', 'flag': '🇹🇼'},
    {'code': 'pt-BR', 'name': 'Portuguese (Brazil)', 'flag': '🇧🇷'},
]

NEURODIVERGENT_CONDITIONS = [
    {'value': 'adhd', 'label': 'ADHD (Attention Deficit Hyperactivity Disorder)'},
    {'value': 'autism', 'label': 'Autism Spectrum Disorder'},
    {'value': 'dyslexia', 'label': 'Dyslexia'},
    {'value': 'dyscalculia', 'label': 'Dyscalculia'},
    {'value': 'dyspraxia', 'label': 'Dyspraxia'},
    {'value': 'ocd', 'label': 'Obsessive Compulsive Disorder'},
    {'value': 'tourettes', 'label': 'Tourette Syndrome'},
    {'value': 'bipolar', 'label': 'Bipolar Disorder'},
    {'value': 'anxiety', 'label': 'Anxiety Disorders'},
    {'value': 'depression', 'label': 'Depression'},
    {'value': 'ptsd', 'label': 'PTSD'},
    {'value': 'other', 'label': 'Other (please specify)'}
]

MENTAL_HEALTH_GOALS = [
    {'value': 'anxiety_management', 'label': 'Managing Anxiety', 'icon': '🧘'},
    {'value': 'depression_support', 'label': 'Depression Support', 'icon': '💙'},
    {'value': 'mood_tracking', 'label': 'Mood Tracking', 'icon': '📈'},
    {'value': 'addiction_recovery', 'label': 'Addiction Recovery', 'icon': '🤝'},
    {'value': 'trauma_healing', 'label': 'Trauma Healing', 'icon': '🌱'},
    {'value': 'stress_reduction', 'label': 'Stress Reduction', 'icon': '🕯️'},
    {'value': 'emotional_regulation', 'label': 'Emotional Regulation', 'icon': '⚖️'},
    {'value': 'relationship_skills', 'label': 'Relationship Skills', 'icon': '❤️'},
    {'value': 'self_esteem', 'label': 'Self-Esteem Building', 'icon': '✨'},
    {'value': 'mindfulness', 'label': 'Mindfulness Practice', 'icon': '🧠'},
    {'value': 'crisis_support', 'label': 'Crisis Support', 'icon': '🆘'},
    {'value': 'general_wellness', 'label': 'General Mental Wellness', 'icon': '🌈'}
]

HEALTH_TRACKING_OPTIONS = [
    {'value': 'mood', 'label': 'Daily Mood', 'icon': '😊'},
    {'value': 'sleep', 'label': 'Sleep Patterns', 'icon': '😴'},
    {'value': 'exercise', 'label': 'Physical Activity', 'icon': '🏃'},
    {'value': 'medication', 'label': 'Medication Tracking', 'icon': '💊'},
    {'value': 'symptoms', 'label': 'Symptom Tracking', 'icon': '📋'},
    {'value': 'energy', 'label': 'Energy Levels', 'icon': '⚡'},
    {'value': 'anxiety', 'label': 'Anxiety Levels', 'icon': '😰'},
    {'value': 'social', 'label': 'Social Interactions', 'icon': '👥'},
    {'value': 'therapy', 'label': 'Therapy Sessions', 'icon': '🗣️'},
    {'value': 'habits', 'label': 'Daily Habits', 'icon': '✅'}
]

WELLNESS_GOALS = [
    {'value': 'exercise_routine', 'label': 'Regular Exercise', 'icon': '💪'},
    {'value': 'meditation', 'label': 'Daily Meditation', 'icon': '🧘'},
    {'value': 'sleep_hygiene', 'label': 'Better Sleep', 'icon': '🛌'},
    {'value': 'nutrition', 'label': 'Healthy Eating', 'icon': '🥗'},
    {'value': 'hydration', 'label': 'Stay Hydrated', 'icon': '💧'},
    {'value': 'social_connection', 'label': 'Social Connections', 'icon': '🤝'},
    {'value': 'creative_expression', 'label': 'Creative Activities', 'icon': '🎨'},
    {'value': 'nature_time', 'label': 'Time in Nature', 'icon': '🌳'},
    {'value': 'learning', 'label': 'Continuous Learning', 'icon': '📚'},
    {'value': 'gratitude', 'label': 'Gratitude Practice', 'icon': '🙏'}
]

# ===== MAIN SETUP ROUTES =====

@setup_bp.route('/')
def index():
    """Setup wizard entry point - redirect to appropriate step"""
    user_id = get_user_id()
    
    # Check if setup is already completed
    if setup_service.is_setup_completed(user_id):
        return redirect(url_for('main.dashboard'))
    
    # Get current setup data
    setup_data = setup_service.get_setup_data(user_id)
    next_step = setup_data.get('next_step', 'welcome')
    
    # Redirect to current step
    return redirect(url_for(f'setup.{next_step}'))

@setup_bp.route('/welcome')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def welcome():
    """Welcome step - introduction to setup wizard"""
    user_id = get_user_id()
    progress = setup_service.get_step_progress(user_id)
    
    return render_template('setup/welcome.html', 
                         progress=progress,
                         user=session.get('user'))

@setup_bp.route('/welcome/save', methods=['POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def welcome_save():
    """Save welcome step and proceed"""
    user_id = get_user_id()
    setup_service.update_setup_step(user_id, 'welcome')
    return redirect(url_for('setup.languages'))

# ===== LANGUAGES STEP =====

@setup_bp.route('/languages')
def languages():
    """Language preferences step"""
    user_id = get_user_id()
    progress = setup_service.get_step_progress(user_id)
    setup_data = setup_service.get_setup_data(user_id)
    preferences = setup_data.get('preferences', {})
    
    return render_template('setup/languages.html',
                         progress=progress,
                         languages=LANGUAGE_OPTIONS,
                         preferences=preferences)

@setup_bp.route('/languages/save', methods=['POST'])
def languages_save():
    """Save language preferences"""
    user_id = get_user_id()
    
    data = {
        'primary_language': request.form.get('primary_language', 'en-US'),
        'secondary_languages': request.form.getlist('secondary_languages'),
        'learning_languages': request.form.getlist('learning_languages')
    }
    
    setup_service.update_setup_step(user_id, 'languages', data)
    return redirect(url_for('setup.neurodivergent'))

# ===== NEURODIVERGENT STEP =====

@setup_bp.route('/neurodivergent')
def neurodivergent():
    """Neurodivergent support step"""
    user_id = get_user_id()
    progress = setup_service.get_step_progress(user_id)
    setup_data = setup_service.get_setup_data(user_id)
    preferences = setup_data.get('preferences', {})
    
    return render_template('setup/neurodivergent.html',
                         progress=progress,
                         conditions=NEURODIVERGENT_CONDITIONS,
                         preferences=preferences)

@setup_bp.route('/neurodivergent/save', methods=['POST'])
def neurodivergent_save():
    """Save neurodivergent preferences"""
    user_id = get_user_id()
    
    is_neurodivergent = request.form.get('is_neurodivergent') == 'yes'
    conditions = request.form.getlist('conditions') if is_neurodivergent else []
    other_condition = request.form.get('other_condition', '').strip()
    
    if other_condition and 'other' in conditions:
        conditions.remove('other')
        conditions.append(f"other:{other_condition}")
    
    data = {
        'is_neurodivergent': is_neurodivergent,
        'conditions': conditions
    }
    
    setup_service.update_setup_step(user_id, 'neurodivergent', data)
    return redirect(url_for('setup.mental_health'))

# ===== MENTAL HEALTH STEP =====

@setup_bp.route('/mental-health')
def mental_health():
    """Mental health goals step"""
    user_id = get_user_id()
    progress = setup_service.get_step_progress(user_id)
    setup_data = setup_service.get_setup_data(user_id)
    preferences = setup_data.get('preferences', {})
    
    return render_template('setup/mental_health.html',
                         progress=progress,
                         goals=MENTAL_HEALTH_GOALS,
                         preferences=preferences)

@setup_bp.route('/mental-health/save', methods=['POST'])
def mental_health_save():
    """Save mental health preferences"""
    user_id = get_user_id()
    
    data = {
        'goals': request.form.getlist('goals'),
        'therapeutic_approach': request.form.get('therapeutic_approach', 'integrated'),
        'crisis_support': request.form.get('crisis_support') == 'yes'
    }
    
    setup_service.update_setup_step(user_id, 'mental_health', data)
    return redirect(url_for('setup.ai_assistant'))

# ===== AI ASSISTANT STEP =====

@setup_bp.route('/ai-assistant')
def ai_assistant():
    """AI assistant preferences step"""
    user_id = get_user_id()
    progress = setup_service.get_step_progress(user_id)
    setup_data = setup_service.get_setup_data(user_id)
    preferences = setup_data.get('preferences', {})
    
    return render_template('setup/ai_assistant.html',
                         progress=progress,
                         preferences=preferences)

@setup_bp.route('/ai-assistant/save', methods=['POST'])
def ai_assistant_save():
    """Save AI assistant preferences"""
    user_id = get_user_id()
    
    data = {
        'personality': request.form.get('personality', 'empathetic'),
        'tone': request.form.get('tone', 'compassionate'),
        'communication_style': request.form.get('communication_style', 'balanced'),
        'assistance_level': request.form.get('assistance_level', 'responsive')
    }
    
    setup_service.update_setup_step(user_id, 'ai_assistant', data)
    return redirect(url_for('setup.health_wellness'))

# ===== HEALTH & WELLNESS STEP =====

@setup_bp.route('/health-wellness')
def health_wellness():
    """Health and wellness step"""
    user_id = get_user_id()
    progress = setup_service.get_step_progress(user_id)
    setup_data = setup_service.get_setup_data(user_id)
    preferences = setup_data.get('preferences', {})
    
    return render_template('setup/health_wellness.html',
                         progress=progress,
                         health_options=HEALTH_TRACKING_OPTIONS,
                         wellness_goals=WELLNESS_GOALS,
                         preferences=preferences)

@setup_bp.route('/health-wellness/save', methods=['POST'])
def health_wellness_save():
    """Save health and wellness preferences"""
    user_id = get_user_id()
    
    # Build reminder preferences
    reminders = {}
    if request.form.get('medication_reminders') == 'yes':
        reminders['medication'] = {
            'enabled': True,
            'times': request.form.getlist('medication_times')
        }
    if request.form.get('therapy_reminders') == 'yes':
        reminders['therapy'] = {'enabled': True}
    if request.form.get('selfcare_reminders') == 'yes':
        reminders['selfcare'] = {'enabled': True}
    
    data = {
        'health_tracking': request.form.getlist('health_tracking'),
        'wellness_goals': request.form.getlist('wellness_goals'),
        'reminders': reminders
    }
    
    setup_service.update_setup_step(user_id, 'health_wellness', data)
    return redirect(url_for('setup.theme_accessibility'))

# ===== THEME & ACCESSIBILITY STEP =====

@setup_bp.route('/theme-accessibility')
def theme_accessibility():
    """Theme and accessibility step"""
    user_id = get_user_id()
    progress = setup_service.get_step_progress(user_id)
    setup_data = setup_service.get_setup_data(user_id)
    preferences = setup_data.get('preferences', {})
    
    return render_template('setup/theme_accessibility.html',
                         progress=progress,
                         preferences=preferences)

@setup_bp.route('/theme-accessibility/save', methods=['POST'])
def theme_accessibility_save():
    """Save theme and accessibility preferences"""
    user_id = get_user_id()
    
    # Build motor accessibility preferences
    motor_accessibility = {}
    if request.form.get('large_buttons') == 'yes':
        motor_accessibility['large_buttons'] = True
    if request.form.get('gesture_controls') == 'yes':
        motor_accessibility['gesture_controls'] = True
    if request.form.get('keyboard_shortcuts') == 'yes':
        motor_accessibility['keyboard_shortcuts'] = True
    
    data = {
        'theme': request.form.get('theme', 'auto'),
        'color_scheme': request.form.get('color_scheme', 'blue'),
        'font_size': request.form.get('font_size', 'medium'),
        'high_contrast': request.form.get('high_contrast') == 'yes',
        'voice_enabled': request.form.get('voice_enabled') == 'yes',
        'voice_mode': request.form.get('voice_mode', 'push-to-talk'),
        'motor_accessibility': motor_accessibility,
        'cognitive_support': request.form.get('cognitive_support', 'standard')
    }
    
    setup_service.update_setup_step(user_id, 'theme_accessibility', data)
    return redirect(url_for('setup.notifications_privacy'))

# ===== NOTIFICATIONS & PRIVACY STEP =====

@setup_bp.route('/notifications-privacy')
def notifications_privacy():
    """Notifications and privacy step"""
    user_id = get_user_id()
    progress = setup_service.get_step_progress(user_id)
    setup_data = setup_service.get_setup_data(user_id)
    preferences = setup_data.get('preferences', {})
    
    return render_template('setup/notifications_privacy.html',
                         progress=progress,
                         preferences=preferences)

@setup_bp.route('/notifications-privacy/save', methods=['POST'])
def notifications_privacy_save():
    """Save notifications and privacy preferences"""
    user_id = get_user_id()
    
    # Build sharing preferences
    sharing = {}
    if request.form.get('family_sharing') == 'yes':
        sharing['family'] = True
    if request.form.get('progress_sharing') == 'yes':
        sharing['progress'] = True
    if request.form.get('anonymous_data') == 'yes':
        sharing['anonymous_analytics'] = True
    
    data = {
        'notification_frequency': request.form.get('notification_frequency', 'medium'),
        'privacy_level': request.form.get('privacy_level', 'full'),
        'sharing': sharing
    }
    
    setup_service.update_setup_step(user_id, 'notifications_privacy', data)
    return redirect(url_for('setup.integrations'))

# ===== INTEGRATIONS STEP =====

@setup_bp.route('/integrations')
def integrations():
    """Integrations step"""
    user_id = get_user_id()
    progress = setup_service.get_step_progress(user_id)
    setup_data = setup_service.get_setup_data(user_id)
    preferences = setup_data.get('preferences', {})
    
    return render_template('setup/integrations.html',
                         progress=progress,
                         preferences=preferences)

@setup_bp.route('/integrations/save', methods=['POST'])
def integrations_save():
    """Save integration preferences"""
    user_id = get_user_id()
    
    # Build Google services preferences
    google_services = {}
    for service in ['calendar', 'tasks', 'keep', 'drive', 'gmail']:
        if request.form.get(f'google_{service}') == 'yes':
            google_services[service] = True
    
    # Build external integrations
    external = {}
    for integration in ['banking', 'fitness', 'health_apps']:
        if request.form.get(f'external_{integration}') == 'yes':
            external[integration] = True
    
    data = {
        'google_services': google_services,
        'spotify_enabled': request.form.get('spotify_enabled') == 'yes',
        'external': external,
        'budget_tracking': request.form.get('budget_tracking') == 'yes',
        'financial_privacy': request.form.get('financial_privacy', 'full'),
        'family_features': request.form.get('family_features') == 'yes',
        'collaboration_level': request.form.get('collaboration_level', 'private')
    }
    
    setup_service.update_setup_step(user_id, 'integrations', data)
    return redirect(url_for('setup.emergency_safety'))

# ===== EMERGENCY & SAFETY STEP =====

@setup_bp.route('/emergency-safety')
def emergency_safety():
    """Emergency and safety step"""
    user_id = get_user_id()
    progress = setup_service.get_step_progress(user_id)
    setup_data = setup_service.get_setup_data(user_id)
    preferences = setup_data.get('preferences', {})
    
    return render_template('setup/emergency_safety.html',
                         progress=progress,
                         preferences=preferences)

@setup_bp.route('/emergency-safety/save', methods=['POST'])
def emergency_safety_save():
    """Save emergency and safety preferences"""
    user_id = get_user_id()
    
    # Build emergency contacts list
    emergency_contacts = []
    contact_names = request.form.getlist('contact_name')
    contact_phones = request.form.getlist('contact_phone')
    contact_relationships = request.form.getlist('contact_relationship')
    
    for i in range(len(contact_names)):
        if contact_names[i].strip() and contact_phones[i].strip():
            emergency_contacts.append({
                'name': contact_names[i].strip(),
                'phone': contact_phones[i].strip(),
                'relationship': contact_relationships[i] if i < len(contact_relationships) else ''
            })
    
    data = {
        'emergency_contacts': emergency_contacts,
        'safety_planning': request.form.get('safety_planning') == 'yes',
        'location_services': request.form.get('location_services') == 'yes'
    }
    
    setup_service.update_setup_step(user_id, 'emergency_safety', data)
    return redirect(url_for('setup.features_guide'))

# ===== FEATURES GUIDE STEP =====

@setup_bp.route('/features-guide')
def features_guide():
    """Features guide and FAQ step"""
    user_id = get_user_id()
    progress = setup_service.get_step_progress(user_id)
    setup_data = setup_service.get_setup_data(user_id)
    preferences = setup_data.get('preferences', {})
    
    return render_template('setup/features_guide.html',
                         progress=progress,
                         preferences=preferences)

@setup_bp.route('/features-guide/save', methods=['POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def features_guide_save():
    """Complete features guide step"""
    user_id = get_user_id()
    setup_service.update_setup_step(user_id, 'features_guide')
    return redirect(url_for('setup.complete'))

# ===== COMPLETION STEP =====

@setup_bp.route('/complete')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def complete():
    """Setup completion step"""
    user_id = get_user_id()
    progress = setup_service.get_step_progress(user_id)
    setup_data = setup_service.get_setup_data(user_id)
    
    # Mark as completed if not already
    if not setup_data.get('is_completed', False):
        setup_service.update_setup_step(user_id, 'complete')
    
    return render_template('setup/complete.html',
                         progress=progress,
                         setup_data=setup_data)

# ===== API ENDPOINTS =====

@setup_bp.route('/api/progress')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def api_progress():
    """Get setup progress via API"""
    user_id = get_user_id()
    progress = setup_service.get_step_progress(user_id)
    return jsonify(progress)

@setup_bp.route('/api/skip-step', methods=['POST'])
def api_skip_step():
    """Skip current step"""
    user_id = get_user_id()
    step = request.json.get('step')
    
    if step and step in setup_service.SETUP_STEPS:
        setup_service.update_setup_step(user_id, step)
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Invalid step'}), 400

@setup_bp.route('/api/restart')
def api_restart():
    """Restart setup wizard"""
    user_id = get_user_id()
    
    try:
        # Reset progress
        progress = setup_service.get_or_create_setup_progress(user_id)
        progress.current_step = 'welcome'
        progress.completed_steps = []
        progress.is_completed = False
        progress.completed_at = None
        
        from database import db
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error restarting setup: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500