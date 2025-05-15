from flask import session, redirect, url_for, flash, render_template, request
from app import app, db
from flask_login import current_user, login_required
from models import UserSettings, ConversationDifficulty
from utils.adaptive_conversation import set_difficulty

# Import Google auth blueprint
from google_auth import google_auth as google_auth_bp

# Register the Google auth blueprint
app.register_blueprint(google_auth_bp, url_prefix="/auth")

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True
    
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
        # Create a simple dict with session values for template
        settings = {
            'conversation_difficulty': session.get('conversation_difficulty', ConversationDifficulty.INTERMEDIATE.value),
            'enable_voice_responses': session.get('enable_voice_responses', False),
            'preferred_language': session.get('preferred_language', 'en-US'),
            'theme': session.get('theme', 'light')
        }
        
    return render_template('settings.html', settings=settings)

@app.route('/settings', methods=['POST'])
def save_settings():
    """Save user settings"""
    # Get form data
    difficulty = request.form.get('conversation_difficulty', ConversationDifficulty.INTERMEDIATE.value)
    enable_voice = 'enable_voice_responses' in request.form
    language = request.form.get('preferred_language', 'en-US')
    theme = request.form.get('theme', 'light')
    
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
            db.session.add(settings)
        else:
            # Update existing settings
            current_user.settings.conversation_difficulty = difficulty
            current_user.settings.enable_voice_responses = enable_voice
            current_user.settings.preferred_language = language
            current_user.settings.theme = theme
            
        db.session.commit()
        flash('Settings saved successfully', 'success')
    else:
        # For anonymous users, save to session
        session['conversation_difficulty'] = difficulty
        session['enable_voice_responses'] = enable_voice
        session['preferred_language'] = language
        session['theme'] = theme
        flash('Settings saved for this session', 'success')
    
    # Use our utility function to set the difficulty
    set_difficulty(difficulty)
    
    return redirect(url_for('index'))

# Add protection to routes that require login
@app.route('/dashboard')
@login_required
def protected_dashboard():
    from app import dashboard
    return dashboard()

@app.route('/api/doctors', methods=["GET"])
@login_required
def protected_api_get_doctors():
    from app import api_get_doctors
    return api_get_doctors()

@app.route('/api/doctors', methods=["POST"])
@login_required
def protected_api_add_doctor():
    from app import api_add_doctor
    return api_add_doctor()

@app.route('/api/doctors/<int:doctor_id>', methods=["GET"])
@login_required
def protected_api_get_doctor(doctor_id):
    from app import api_get_doctor
    return api_get_doctor(doctor_id)

@app.route('/api/doctors/<int:doctor_id>', methods=["PUT"])
@login_required
def protected_api_update_doctor(doctor_id):
    from app import api_update_doctor
    return api_update_doctor(doctor_id)

@app.route('/api/doctors/<int:doctor_id>', methods=["DELETE"])
@login_required
def protected_api_delete_doctor(doctor_id):
    from app import api_delete_doctor
    return api_delete_doctor(doctor_id)

# We'll add protection to just a few of the API routes for demonstration
# In a real application, you would protect all API routes

# Create a welcome page
@app.route('/welcome')
@login_required
def welcome():
    return f"""
    <h1>Welcome, {current_user.first_name if current_user.first_name else 'User'}!</h1>
    <p>You have successfully logged in via Replit Auth.</p>
    <p>Your email: {current_user.email if current_user.email else 'Not provided'}</p>
    <p><a href="{url_for('index')}">Go to Command Interface</a></p>
    <p><a href="{url_for('protected_dashboard')}">Go to Dashboard</a></p>
    <p><a href="{url_for('google_auth.logout')}">Logout</a></p>
    """