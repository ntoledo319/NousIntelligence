from flask import session, redirect, url_for, flash, render_template, request, abort
from app import app, db
from flask_login import current_user, login_required
from models import UserSettings, ConversationDifficulty
from utils.adaptive_conversation import set_difficulty
from utils.security_helper import (
    csrf_protect, generate_csrf_token, session_timeout_check, 
    sanitize_input, require_https, log_security_event
)
import logging

# Import Google auth blueprint
from google_auth import google_auth as google_auth_bp

# Register the Google auth blueprint
app.register_blueprint(google_auth_bp, url_prefix="/auth")

# Make session permanent, add security headers, and check session timeout
@app.before_request
def request_processor():
    session.permanent = True
    
    # Update session activity timestamp
    if current_user.is_authenticated:
        from datetime import datetime
        session['last_activity'] = datetime.utcnow().timestamp()
    
    # Add security-related headers to all responses
    @app.after_request
    def apply_security_headers(response):
        # Content Security Policy
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' data: https:; font-src 'self' https://cdn.jsdelivr.net;"
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        # XSS Protection
        response.headers['X-XSS-Protection'] = '1; mode=block'
        # Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        # Referrer Policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        # Permissions Policy
        response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
        return response

# Make CSRF token available to all templates
@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf_token())
    
# Settings routes
@app.route('/settings')
def settings_page():
    """Display user settings page"""
    settings = None
    
    # Get settings for logged-in users from database
    if current_user.is_authenticated:
        settings = current_user.settings
    # For anonymous users, get from session if available
    elif 'conversation_difficulty' in session:
        # Get character settings from session
        character_settings = session.get('character_settings', {})
        
        # Create a combined dict with session values for template
        settings = {
            # Basic settings
            'conversation_difficulty': session.get('conversation_difficulty', ConversationDifficulty.INTERMEDIATE.value),
            'enable_voice_responses': session.get('enable_voice_responses', False),
            'preferred_language': session.get('preferred_language', 'en-US'),
            'theme': session.get('theme', 'light'),
            
            # AI character settings
            'ai_name': character_settings.get('ai_name', 'NOUS'),
            'ai_personality': character_settings.get('ai_personality', 'helpful'),
            'ai_formality': character_settings.get('ai_formality', 'casual'),
            'ai_verbosity': character_settings.get('ai_verbosity', 'balanced'),
            'ai_enthusiasm': character_settings.get('ai_enthusiasm', 'moderate'),
            'ai_emoji_usage': character_settings.get('ai_emoji_usage', 'occasional'),
            'ai_voice_type': character_settings.get('ai_voice_type', 'neutral'),
            'ai_backstory': character_settings.get('ai_backstory', '')
        }
        
    # Prepare data for dropdown options    
    personality_options = [
        {'value': 'helpful', 'label': 'Helpful - Practical problem-solving'},
        {'value': 'friendly', 'label': 'Friendly - Warm and approachable'},
        {'value': 'professional', 'label': 'Professional - Efficient and business-like'},
        {'value': 'witty', 'label': 'Witty - Clever with a sense of humor'},
        {'value': 'compassionate', 'label': 'Compassionate - Empathetic and supportive'}
    ]
    
    formality_options = [
        {'value': 'casual', 'label': 'Casual - Relaxed, everyday language'},
        {'value': 'neutral', 'label': 'Neutral - Balanced, adaptable language'},
        {'value': 'formal', 'label': 'Formal - Structured, precise language'}
    ]
    
    verbosity_options = [
        {'value': 'concise', 'label': 'Concise - Brief, to-the-point responses'},
        {'value': 'balanced', 'label': 'Balanced - Complete but mindful of length'},
        {'value': 'detailed', 'label': 'Detailed - Thorough, comprehensive responses'}
    ]
    
    enthusiasm_options = [
        {'value': 'low', 'label': 'Low - Calm, even tone'},
        {'value': 'moderate', 'label': 'Moderate - Appropriate enthusiasm'},
        {'value': 'high', 'label': 'High - Energetic and passionate'}
    ]
    
    emoji_options = [
        {'value': 'none', 'label': 'None - No emojis'},
        {'value': 'occasional', 'label': 'Occasional - Sparing use of emojis'},
        {'value': 'frequent', 'label': 'Frequent - Regular use of emojis'}
    ]
    
    voice_options = [
        {'value': 'neutral', 'label': 'Neutral - Balanced, versatile voice'},
        {'value': 'warm', 'label': 'Warm - Friendly, approachable voice'},
        {'value': 'authoritative', 'label': 'Authoritative - Confident, knowledgeable voice'},
        {'value': 'energetic', 'label': 'Energetic - Upbeat, enthusiastic voice'},
        {'value': 'calm', 'label': 'Calm - Soothing, gentle voice'}
    ]
        
    return render_template(
        'settings.html', 
        settings=settings,
        personality_options=personality_options,
        formality_options=formality_options,
        verbosity_options=verbosity_options,
        enthusiasm_options=enthusiasm_options,
        emoji_options=emoji_options,
        voice_options=voice_options
    )

@app.route('/settings', methods=['POST'])
@csrf_protect
@session_timeout_check
def save_settings():
    """Save user settings"""
    # Get basic form data
    difficulty = request.form.get('conversation_difficulty', ConversationDifficulty.INTERMEDIATE.value)
    enable_voice = 'enable_voice_responses' in request.form
    language = request.form.get('preferred_language', 'en-US')
    theme = request.form.get('theme', 'light')
    
    # Get AI character customization data (with sanitization for security)
    ai_name = sanitize_input(request.form.get('ai_name', 'NOUS'))
    ai_personality = request.form.get('ai_personality', 'helpful')
    ai_formality = request.form.get('ai_formality', 'casual')
    ai_verbosity = request.form.get('ai_verbosity', 'balanced')
    ai_enthusiasm = request.form.get('ai_enthusiasm', 'moderate')
    ai_emoji_usage = request.form.get('ai_emoji_usage', 'occasional')
    ai_voice_type = request.form.get('ai_voice_type', 'neutral')
    ai_backstory = sanitize_input(request.form.get('ai_backstory', ''))
    
    # For logged-in users, save to database
    if current_user.is_authenticated:
        # Create settings if they don't exist
        if not current_user.settings:
            settings = UserSettings()
            settings.user_id = current_user.id
            settings.conversation_difficulty = difficulty
            settings.enable_voice_responses = enable_voice
            settings.preferred_language = language
            settings.theme = theme
            
            # Set AI character fields
            settings.ai_name = ai_name
            settings.ai_personality = ai_personality
            settings.ai_formality = ai_formality
            settings.ai_verbosity = ai_verbosity
            settings.ai_enthusiasm = ai_enthusiasm
            settings.ai_emoji_usage = ai_emoji_usage
            settings.ai_voice_type = ai_voice_type
            settings.ai_backstory = ai_backstory
            
            db.session.add(settings)
        else:
            # Update existing settings
            current_user.settings.conversation_difficulty = difficulty
            current_user.settings.enable_voice_responses = enable_voice
            current_user.settings.preferred_language = language
            current_user.settings.theme = theme
            
            # Update AI character fields
            current_user.settings.ai_name = ai_name
            current_user.settings.ai_personality = ai_personality
            current_user.settings.ai_formality = ai_formality
            current_user.settings.ai_verbosity = ai_verbosity
            current_user.settings.ai_enthusiasm = ai_enthusiasm
            current_user.settings.ai_emoji_usage = ai_emoji_usage
            current_user.settings.ai_voice_type = ai_voice_type
            current_user.settings.ai_backstory = ai_backstory
            
        db.session.commit()
        flash('Settings saved successfully', 'success')
    else:
        # For anonymous users, save to session
        session['conversation_difficulty'] = difficulty
        session['enable_voice_responses'] = enable_voice
        session['preferred_language'] = language
        session['theme'] = theme
        
        # Also save character settings to session
        session['character_settings'] = {
            'ai_name': ai_name,
            'ai_personality': ai_personality,
            'ai_formality': ai_formality,
            'ai_verbosity': ai_verbosity,
            'ai_enthusiasm': ai_enthusiasm,
            'ai_emoji_usage': ai_emoji_usage,
            'ai_voice_type': ai_voice_type,
            'ai_backstory': ai_backstory
        }
        
        flash('Settings saved for this session', 'success')
    
    # Use our utility function to set the difficulty
    set_difficulty(difficulty)
    
    return redirect(url_for('settings_page'))

# Add protection to routes that require login
@app.route('/dashboard')
@login_required
@session_timeout_check
@require_https
def protected_dashboard():
    from app import dashboard
    log_security_event("PAGE_ACCESS", "User accessed dashboard")
    return dashboard()

@app.route('/api/doctors', methods=["GET"])
@login_required
@session_timeout_check
def protected_api_get_doctors():
    from app import api_get_doctors
    log_security_event("API_ACCESS", "User retrieved doctor list")
    return api_get_doctors()

@app.route('/api/doctors', methods=["POST"])
@login_required
@session_timeout_check
@csrf_protect
def protected_api_add_doctor():
    from app import api_add_doctor
    log_security_event("DATA_MODIFICATION", "User added a new doctor")
    return api_add_doctor()

@app.route('/api/doctors/<int:doctor_id>', methods=["GET"])
@login_required
@session_timeout_check
def protected_api_get_doctor(doctor_id):
    from app import api_get_doctor
    log_security_event("API_ACCESS", f"User retrieved doctor id={doctor_id}")
    return api_get_doctor(doctor_id)

@app.route('/api/doctors/<int:doctor_id>', methods=["PUT"])
@login_required
@session_timeout_check
@csrf_protect
def protected_api_update_doctor(doctor_id):
    from app import api_update_doctor
    log_security_event("DATA_MODIFICATION", f"User updated doctor id={doctor_id}")
    return api_update_doctor(doctor_id)

@app.route('/api/doctors/<int:doctor_id>', methods=["DELETE"])
@login_required
@session_timeout_check
@csrf_protect
def protected_api_delete_doctor(doctor_id):
    from app import api_delete_doctor
    log_security_event("DATA_DELETION", f"User deleted doctor id={doctor_id}", severity="WARNING")
    return api_delete_doctor(doctor_id)

# We'll add protection to just a few of the API routes for demonstration
# In a real application, you would protect all API routes

# Create a welcome page
@app.route('/welcome')
@login_required
@session_timeout_check
@require_https
def welcome():
    # Sanitize user data for display
    first_name = sanitize_input(current_user.first_name) if current_user.first_name else 'User'
    email = sanitize_input(current_user.email) if current_user.email else 'Not provided'
    
    # Log access
    log_security_event("PAGE_ACCESS", "User accessed welcome page")
    
    # Use render_template instead of direct HTML for better security and maintainability
    return render_template(
        'welcome.html',
        user_name=first_name,
        user_email=email
    )