from flask import session, redirect, url_for, flash, render_template, request, abort
from app import app, db
from flask_login import current_user, login_required
from models import UserSettings, ConversationDifficulty, User
from utils.adaptive_conversation import set_difficulty
from utils.security_helper import (
    csrf_protect, generate_csrf_token, session_timeout_check, 
    sanitize_input, require_https, log_security_event
)
from utils.setup_wizard import get_setup_progress
import logging
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

# Import other blueprints
from routes.beta_routes import beta_bp
from routes.aa_routes import aa_bp
from routes.amazon_routes import amazon_bp
from routes.setup_routes import setup_bp

# Setup Google OAuth with our new implementation
from new_google_auth import google_auth as google_bp

# Register the blueprints
# Removed google_bp registration to fix authentication conflicts
app.register_blueprint(beta_bp, url_prefix="/beta")
app.register_blueprint(aa_bp, url_prefix="/aa") 
app.register_blueprint(amazon_bp, url_prefix="/amazon")
app.register_blueprint(setup_bp, url_prefix="/setup")

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
    
# Main index route - directs to setup wizard if needed
@app.route('/')
@app.route('/index')
def index():
    """Main landing page with setup wizard redirection if needed"""
    # Check if user is authenticated and needs to complete setup
    if current_user.is_authenticated:
        user_id = str(current_user.id)
        # Get current setup progress
        progress = get_setup_progress(user_id)
        
        # If setup is not yet complete, redirect to setup wizard
        if not progress.get('has_completed_setup', False):
            return redirect(url_for('setup.wizard'))
    
    # Render the main dashboard/index page
    return render_template('index.html', user=current_user)

# Login page
@app.route('/login')
def login_page():
    """Display login page"""
    # If user is already logged in, redirect to home
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Render the login page
    return render_template('login.html')

# Test endpoint for Google OAuth configuration
@app.route('/test-google-auth')
def test_google_auth():
    """Diagnostic endpoint for testing Google OAuth configuration"""
    import json
    import os
    
    # Initialize dictionary
    environment_info = {
        "domain": request.host,
        "protocol": request.scheme,
        "base_url": request.url_root,
        "full_url": request.url,
        "replit_dev_domain": os.environ.get('REPLIT_DEV_DOMAIN', 'Not set')
    }
    
    test_results = {}
    test_results["environment"] = environment_info
    
    # Read Google client configuration
    try:
        with open('client_secret.json', 'r') as f:
            client_config = json.load(f)['web']
            
        # Create OAuth configuration dictionary
        oauth_info = {}
        oauth_info["client_id"] = client_config['client_id']
        oauth_info["redirect_uris"] = client_config['redirect_uris']
        if 'javascript_origins' in client_config:
            oauth_info["javascript_origins"] = client_config['javascript_origins']
        test_results["google_oauth"] = oauth_info
        
        # Generate expected callback URL and check for match
        expected_url = request.url_root.rstrip('/') + "/callback/google"
        test_results["expected_callback_url"] = expected_url
        test_results["registered_callback_matches"] = expected_url in client_config['redirect_uris']
        
    except Exception as e:
        test_results["error"] = str(e)
    
    # Return results as formatted HTML
    html_result = "<h1>Google OAuth Configuration Test</h1>"
    html_result += "<pre>" + json.dumps(test_results, indent=2) + "</pre>"
    
    # Add recommendation if there's a mismatch
    if test_results.get("registered_callback_matches") is False:
        html_result += "<h2>Configuration Issue Detected</h2>"
        html_result += "<p>The callback URL for your current domain does not match what's registered in Google Cloud Console.</p>"
        html_result += "<p>Please add this URL to your authorized redirect URIs in Google Cloud Console:</p>"
        html_result += f"<code>{test_results['expected_callback_url']}</code>"
    
    # Convert result to HTML safely
    # We're using the "safe" filter in render_template to let it know this is intentionally HTML
    return render_template('raw.html', content=html_result)

# Help page
@app.route('/help')
def help_page():
    """Display help page"""
    return render_template('help.html', user=current_user)

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
    # Check if user has completed setup wizard
    user_id = str(current_user.id)
    progress = get_setup_progress(user_id)
    
    # If setup is not yet complete, redirect to setup wizard
    if not progress.get('has_completed_setup', False):
        return redirect(url_for('setup.wizard'))
        
    # Continue to dashboard if setup is complete
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

# Error handlers for the application
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logging.error(f"500 error: {str(e)}")
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden(e):
    """Handle 403 errors"""
    return render_template('errors/403.html'), 403

@app.errorhandler(SQLAlchemyError)
def handle_db_error(e):
    """Handle database errors"""
    logging.error(f"Database error: {str(e)}")
    db.session.rollback()
    return render_template('errors/500.html', error_message="A database error occurred."), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all other exceptions"""
    if isinstance(e, HTTPException):
        return e
    logging.error(f"Unhandled exception: {str(e)}")
    return render_template('errors/500.html', error_message="An unexpected error occurred."), 500